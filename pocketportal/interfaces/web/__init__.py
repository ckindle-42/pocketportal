"""
Web Interface - FastAPI + WebSocket for AgentCore
=================================================

This provides a web-based interface to the unified AgentCore.
Users can chat via browser just like they do via Telegram.

Architecture:
    Browser WebSocket → WebInterface → AgentCore → Response → Browser

Features:
    - Real-time chat via WebSocket
    - Multiple concurrent sessions
    - Same core as Telegram (shared memory, tools, routing)
    - Clean HTML/CSS/JS frontend
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Import the unified core
from pocketportal.core import AgentCoreV2, ProcessingResult

# Import existing config
from pocketportal.config import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="PocketPortal Web",
    description="Web interface for PocketPortal AI Agent",
    version="1.0.0"
)

# CORS middleware (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# GLOBAL STATE
# ============================================================================

# Shared agent core (same instance for all web sessions)
agent_core: Optional[AgentCore] = None

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Session data
sessions: Dict[str, Dict] = {}


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global agent_core
    
    logger.info("=" * 60)
    logger.info("Starting PocketPortal Web Interface")
    logger.info("=" * 60)
    
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
    logger.info("Web interface ready!")
    logger.info("Open http://localhost:8000 in your browser")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global agent_core
    
    logger.info("Shutting down web interface...")
    
    if agent_core:
        await agent_core.cleanup()
    
    logger.info("Shutdown complete")


# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - serve static HTML"""
    html_file = Path(__file__).parent.parent / "web_static" / "index.html"
    
    if not html_file.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "Frontend not found. Please create web_static/index.html"}
        )
    
    return HTMLResponse(content=html_file.read_text())


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if not agent_core:
        raise HTTPException(status_code=503, detail="Agent core not initialized")
    
    stats = agent_core.get_stats()
    
    return {
        "status": "healthy",
        "uptime_seconds": stats['uptime_seconds'],
        "messages_processed": stats['messages_processed'],
        "tools_executed": stats['tools_executed']
    }


@app.get("/api/tools")
async def get_tools():
    """Get list of available tools"""
    if not agent_core:
        raise HTTPException(status_code=503, detail="Agent core not initialized")
    
    tools = agent_core.get_tool_list()
    return {"tools": tools}


@app.get("/api/stats")
async def get_stats():
    """Get processing statistics"""
    if not agent_core:
        raise HTTPException(status_code=503, detail="Agent core not initialized")
    
    stats = agent_core.get_stats()
    return stats


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat
    
    Protocol:
        Client → Server: {"type": "message", "content": "user message"}
        Server → Client: {"type": "response", "content": "...", "model": "...", "time": ...}
        Server → Client: {"type": "error", "error": "..."}
    """
    await websocket.accept()
    active_connections[session_id] = websocket
    
    # Initialize session
    if session_id not in sessions:
        sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'message_count': 0
        }
    
    logger.info(f"WebSocket connected: session_id={session_id}")
    
    # Send welcome message
    await websocket.send_json({
        "type": "system",
        "content": "Connected to PocketPortal! Send a message to get started.",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if data.get('type') == 'message':
                message = data.get('content', '').strip()
                
                if not message:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Empty message"
                    })
                    continue
                
                logger.info(f"Received from {session_id}: {message[:50]}...")
                
                # Update session
                sessions[session_id]['message_count'] += 1
                
                # Send typing indicator
                await websocket.send_json({
                    "type": "typing",
                    "typing": True
                })
                
                try:
                    # Process with agent core
                    result: ProcessingResult = await agent_core.process_message(
                        chat_id=f"web_{session_id}",
                        message=message,
                        interface="web",
                        user_context={'session_id': session_id}
                    )
                    
                    # Send response
                    await websocket.send_json({
                        "type": "response",
                        "content": result.response,
                        "model": result.model_used,
                        "time": result.execution_time,
                        "tools_used": result.tools_used,
                        "timestamp": datetime.now().isoformat(),
                        "success": result.success
                    })
                    
                    # Send warnings if any
                    if result.warnings:
                        await websocket.send_json({
                            "type": "warning",
                            "warnings": result.warnings
                        })
                
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Error processing message: {str(e)}"
                    })
            
            elif data.get('type') == 'ping':
                # Keep-alive ping
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session_id={session_id}")
        if session_id in active_connections:
            del active_connections[session_id]
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if session_id in active_connections:
            del active_connections[session_id]


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
        port=8000,
        log_level="info",
        access_log=True
    )
