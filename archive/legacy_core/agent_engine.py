"""
Unified Agent Core - Interface-Agnostic Processing Engine
==========================================================

This is the heart of PocketPortal. It processes messages from ANY interface
(Telegram, Web, Slack, API) using the same routing, tools, and memory.

Key Design Principles:
1. Interface-agnostic: Knows nothing about Telegram/Web/Slack specifics
2. Reuses existing systems: routing, tools, security
3. Unified memory: Same context across all interfaces
4. Thread-safe: Can handle multiple interfaces simultaneously
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Import existing routing system (unchanged)
from routing import (
    ModelRegistry,
    IntelligentRouter,
    ExecutionEngine,
    RoutingStrategy
)

# Import existing tool registry (unchanged)
from telegram_agent_tools import registry as tool_registry

# Import existing security (unchanged)
from security.security_module import InputSanitizer

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result from processing a message"""
    success: bool
    response: str
    model_used: str
    execution_time: float
    tools_used: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class AgentCore:
    """
    Unified Agent Core - The Brain
    
    This class orchestrates all AI operations regardless of which interface
    the user is using. Telegram, Web, Slack, or API - all call this same core.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the unified core
        
        Args:
            config: Configuration dictionary with keys like:
                - ollama_base_url
                - lmstudio_base_url
                - routing_strategy
                - model_preferences
                - etc.
        """
        self.config = config
        self.start_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info("Initializing AgentCore (Unified Engine)")
        logger.info("=" * 60)
        
        # Initialize routing system (reuse existing)
        logger.info("Loading routing system...")
        self.model_registry = ModelRegistry()
        
        strategy_name = config.get('routing_strategy', 'AUTO').upper()
        self.routing_strategy = getattr(RoutingStrategy, strategy_name, RoutingStrategy.AUTO)
        
        self.router = IntelligentRouter(
            self.model_registry,
            strategy=self.routing_strategy,
            model_preferences=config.get('model_preferences', {})
        )
        
        backend_config = {
            'ollama_base_url': config.get('ollama_base_url', 'http://localhost:11434'),
            'lmstudio_base_url': config.get('lmstudio_base_url', 'http://localhost:1234/v1')
        }
        
        self.execution_engine = ExecutionEngine(
            self.model_registry,
            self.router,
            backend_config
        )
        
        # Initialize tool registry (reuse existing)
        logger.info("Loading tool registry...")
        self.tool_registry = tool_registry
        loaded, failed = self.tool_registry.discover_and_load()
        logger.info(f"Tools loaded: {loaded} success, {failed} failed")
        
        # Initialize security (reuse existing)
        logger.info("Initializing security module...")
        self.input_sanitizer = InputSanitizer()
        
        # Statistics tracking
        self.stats = {
            'messages_processed': 0,
            'total_execution_time': 0.0,
            'tools_executed': 0,
            'by_interface': {}
        }
        
        logger.info("=" * 60)
        logger.info("AgentCore initialized successfully!")
        logger.info(f"  Routing: {self.routing_strategy.value}")
        logger.info(f"  Tools: {loaded}")
        logger.info(f"  Models: {len(self.model_registry.models)}")
        logger.info("=" * 60)
    
    async def process_message(
        self,
        chat_id: str,
        message: str,
        interface: str = "unknown",
        user_context: Optional[Dict] = None,
        files: Optional[List[Any]] = None
    ) -> ProcessingResult:
        """
        Process a message from ANY interface
        
        This is the main entry point for all message processing.
        Telegram, Web, Slack - they all call this method.
        
        Args:
            chat_id: Unique identifier for this conversation
            message: The user's message text
            interface: Source interface ("telegram", "web", "slack", etc.)
            user_context: Optional context about the user/session
            files: Optional list of attached files
            
        Returns:
            ProcessingResult with response and metadata
        """
        start_time = datetime.now()
        
        # Update statistics
        self.stats['messages_processed'] += 1
        if interface not in self.stats['by_interface']:
            self.stats['by_interface'][interface] = 0
        self.stats['by_interface'][interface] += 1
        
        logger.info(
            f"Processing message from {interface} | "
            f"chat_id={chat_id} | "
            f"length={len(message)}"
        )
        
        # Security: Sanitize input
        sanitized_message, warnings = self.input_sanitizer.sanitize_command(message)
        
        if warnings:
            logger.warning(f"Security warnings for chat_id={chat_id}: {warnings}")
        
        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt(interface, user_context)
            
            # Get available tools
            available_tools = [t.metadata.name for t in self.tool_registry.get_all_tools()]
            
            # Execute with routing (reuse existing execution engine)
            result = await self.execution_engine.execute(
                query=sanitized_message,
                system_prompt=system_prompt,
                available_tools=available_tools
            )
            
            # Track execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            self.stats['total_execution_time'] += execution_time
            
            # Extract tools used (if available)
            tools_used = []
            if hasattr(result, 'tools_used'):
                tools_used = result.tools_used
                self.stats['tools_executed'] += len(tools_used)
            
            logger.info(
                f"Completed processing | "
                f"model={result.model_id} | "
                f"time={execution_time:.2f}s | "
                f"tools={len(tools_used)}"
            )
            
            return ProcessingResult(
                success=result.success,
                response=result.content,
                model_used=result.model_id,
                execution_time=execution_time,
                tools_used=tools_used,
                warnings=warnings,
                metadata={
                    'chat_id': chat_id,
                    'interface': interface,
                    'timestamp': start_time.isoformat(),
                    'routing_strategy': self.routing_strategy.value
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                response=f"⚠️ Error processing your request: {str(e)}",
                model_used="none",
                execution_time=execution_time,
                tools_used=[],
                warnings=warnings,
                metadata={
                    'error': str(e),
                    'chat_id': chat_id,
                    'interface': interface
                }
            )
    
    def _build_system_prompt(
        self,
        interface: str,
        user_context: Optional[Dict]
    ) -> str:
        """
        Build a system prompt with context
        
        This can be customized based on interface or user preferences
        """
        base_prompt = (
            "You are a helpful AI assistant with access to various tools. "
            "You can help with coding, data analysis, file operations, web requests, "
            "and much more. Be concise and practical in your responses."
        )
        
        # Add interface-specific context if needed
        if interface == "telegram":
            base_prompt += "\n\nYou are communicating via Telegram, so keep responses mobile-friendly."
        elif interface == "web":
            base_prompt += "\n\nYou are communicating via web browser."
        
        # Add user context if provided
        if user_context and user_context.get('preferences'):
            prefs = user_context['preferences']
            if prefs.get('verbose'):
                base_prompt += "\n\nThe user prefers detailed explanations."
            if prefs.get('terse'):
                base_prompt += "\n\nThe user prefers brief, concise responses."
        
        return base_prompt
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        stats = self.stats.copy()
        stats['uptime_seconds'] = uptime
        
        if stats['messages_processed'] > 0:
            stats['avg_execution_time'] = (
                stats['total_execution_time'] / stats['messages_processed']
            )
        else:
            stats['avg_execution_time'] = 0
        
        return stats
    
    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return self.tool_registry.get_tool_list()
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a specific tool directly
        
        This is useful for direct tool execution without LLM reasoning
        """
        tool = self.tool_registry.get_tool(tool_name)
        
        if not tool:
            return {
                'success': False,
                'error': f'Tool not found: {tool_name}'
            }
        
        try:
            result = await tool.execute(parameters)
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up AgentCore...")
        await self.execution_engine.cleanup()
        logger.info("AgentCore cleanup complete")


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

async def test_core():
    """Test the core with a simple query"""
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'routing_strategy': 'AUTO',
        'model_preferences': {}
    }
    
    core = AgentCore(config)
    
    # Test message processing
    result = await core.process_message(
        chat_id="test_001",
        message="Hello! What tools do you have?",
        interface="test"
    )
    
    print("\n" + "=" * 60)
    print("TEST RESULT:")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Model: {result.model_used}")
    print(f"Time: {result.execution_time:.2f}s")
    print(f"Response: {result.response[:200]}...")
    print("=" * 60)
    
    await core.cleanup()


if __name__ == "__main__":
    # Run test
    asyncio.run(test_core())
