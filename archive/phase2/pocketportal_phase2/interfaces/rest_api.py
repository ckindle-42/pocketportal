"""
REST API Interface - RESTful API for AgentCore
==============================================

Provides a clean REST API for the unified AgentCore.
Useful for integrations, mobile apps, and third-party services.

Endpoints:
- POST /api/v1/chat - Send message and get response
- GET /api/v1/tools - List available tools
- POST /api/v1/tools/{tool_name}/execute - Execute specific tool
- GET /api/v1/stats - Get processing statistics
- GET /api/v1/health - Health check

Authentication via API key.
"""

import asyncio
import logging
import os
import sys
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import the unified core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import AgentCore, ProcessingResult

# Import existing config
from config_validator import load_and_validate_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# API MODELS (Request/Response schemas)
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default="api_user")
    context: Optional[Dict[str, Any]] = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What's the weather like?",
                "session_id": "session_123",
                "user_id": "user_456"
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema"""
    success: bool
    response: str
    model_used: str
    execution_time: float
    tools_used: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    timestamp: str


class ToolExecutionRequest(BaseModel):
    """Tool execution request schema"""
    parameters: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "parameters": {
                    "text": "Hello",
                    "style": "banner"
                }
            }
        }


class ToolExecutionResponse(BaseModel):
    """Tool execution response schema"""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    uptime_seconds: float
    messages_processed: int
    tools_executed: int
    timestamp: str


# ============================================================================
# AUTHENTICATION
# ============================================================================

api_key_header = APIKeyHeader(name="X-API-Key")

# Valid API keys (in production, store in database)
VALID_API_KEYS = set()

def load_api_keys():
    """Load API keys from environment or generate default"""
    global VALID_API_KEYS
    
    # Load from environment
    keys_str = os.getenv("API_KEYS", "")
    if keys_str:
        VALID_API_KEYS = set(keys_str.split(","))
    else:
        # Generate a default key
        default_key = secrets.token_urlsafe(32)
        VALID_API_KEYS = {default_key}
        logger.warning(f"No API keys configured. Generated default key: {default_key}")
        logger.warning("Add API_KEYS=your_key_here to .env for production")
    
    logger.info(f"Loaded {len(VALID_API_KEYS)} API key(s)")


async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key"""
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="PocketPortal API",
    description="RESTful API for PocketPortal AI Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent core
agent_core: Optional[AgentCore] = None


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global agent_core
    
    logger.info("=" * 60)
    logger.info("Starting PocketPortal REST API")
    logger.info("=" * 60)
    
    # Load API keys
    load_api_keys()
    
    # Load configuration
    config = load_and_validate_config()
    if not config:
        raise RuntimeError("Invalid configuration")
    
    # Build core config
    core_config = {
        'ollama_base_url': config.ollama_base_url,
        'lmstudio_base_url': config.lmstudio_base_url,
        'routing_strategy': config.routing_strategy,
        'model_preferences': {
            'trivial': [m.strip() for m in config.model_pref_trivial.split(',') if m.strip()],
            'simple': [m.strip() for m in config.model_pref_simple.split(',') if m.strip()],
            'moderate': [m.strip() for m in config.model_pref_moderate.split(',') if m.strip()],
            'complex': [m.strip() for m in config.model_pref_complex.split(',') if m.strip()],
            'expert': [m.strip() for m in config.model_pref_expert.split(',') if m.strip()],
            'code': [m.strip() for m in config.model_pref_code.split(',') if m.strip()]
        }
    }
    
    # Initialize agent core
    agent_core = AgentCore(core_config)
    
    logger.info("=" * 60)
    logger.info("REST API ready!")
    logger.info("Visit http://localhost:8001/docs for API documentation")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global agent_core
    
    logger.info("Shutting down REST API...")
    
    if agent_core:
        await agent_core.cleanup()
    
    logger.info("Shutdown complete")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PocketPortal API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/v1/health"
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Send a message and get AI response.
    
    This endpoint processes the message through the unified AgentCore,
    which handles routing, tool execution, and response generation.
    """
    if not agent_core:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent core not initialized"
        )
    
    try:
        # Process with agent core
        result: ProcessingResult = await agent_core.process_message(
            chat_id=request.session_id or f"api_{request.user_id}",
            message=request.message,
            interface="api",
            user_context=request.context or {'user_id': request.user_id}
        )
        
        return ChatResponse(
            success=result.success,
            response=result.response,
            model_used=result.model_used,
            execution_time=result.execution_time,
            tools_used=result.tools_used,
            warnings=result.warnings,
            metadata=result.metadata,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/tools")
async def get_tools(api_key: str = Depends(verify_api_key)):
    """
    Get list of available tools.
    
    Returns metadata for all registered tools including their
    names, descriptions, categories, and parameters.
    """
    if not agent_core:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent core not initialized"
        )
    
    try:
        tools = agent_core.get_tool_list()
        return {
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"Tools list error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/v1/tools/{tool_name}/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    tool_name: str,
    request: ToolExecutionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Execute a specific tool directly.
    
    This endpoint bypasses the LLM and executes the tool directly
    with the provided parameters. Useful for programmatic tool access.
    """
    if not agent_core:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent core not initialized"
        )
    
    try:
        result = await agent_core.execute_tool(tool_name, request.parameters)
        
        return ToolExecutionResponse(
            success=result.get('success', False),
            result=result.get('result'),
            error=result.get('error'),
            metadata=result.get('metadata')
        )
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """
    Get processing statistics.
    
    Returns metrics about message processing, tool execution,
    and performance across all interfaces.
    """
    if not agent_core:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent core not initialized"
        )
    
    try:
        stats = agent_core.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint (no auth required).
    
    Returns basic health status of the service.
    """
    if not agent_core:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent core not initialized"
        )
    
    try:
        stats = agent_core.get_stats()
        
        return HealthResponse(
            status="healthy",
            uptime_seconds=stats['uptime_seconds'],
            messages_processed=stats['messages_processed'],
            tools_executed=stats['tools_executed'],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Ensure directories exist
    Path("logs").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    Path("browser_data").mkdir(exist_ok=True)
    
    # Run server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info",
        access_log=True
    )
