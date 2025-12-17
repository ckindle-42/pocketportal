"""
Unified Agent Core v2.0 - Refactored with Dependency Injection
===============================================================

This is the heart of PocketPortal 4.0 - truly modular and production-ready.

Key Improvements:
1. ✅ Dependency Injection - All dependencies passed in, easily testable
2. ✅ Structured Errors - Custom exceptions instead of string returns
3. ✅ Context Management - Shared history across interfaces
4. ✅ Event Bus - Real-time feedback to interfaces
5. ✅ Structured Logging - JSON logs with trace IDs
6. ✅ Externalized Prompts - No hardcoded strings
7. ✅ Security Middleware - No data reaches core without validation

Architecture:
    Interface → SecurityMiddleware → AgentCore → Router → LLM
                                       ↓
                                  ContextManager
                                  EventBus
                                  PromptManager
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Import existing routing system
from pocketportal.routing import (
    ModelRegistry,
    IntelligentRouter,
    ExecutionEngine,
    RoutingStrategy
)

# Import tool registry
from pocketportal.tools import registry as tool_registry

# Import new unified components
from .context_manager import ContextManager
from .event_bus import EventBus, EventType, EventEmitter
from .prompt_manager import PromptManager
from .structured_logger import get_logger, TraceContext
from .exceptions import (
    PocketPortalError,
    ModelNotAvailableError,
    ToolExecutionError
)

logger = get_logger('AgentCore')


@dataclass
class ProcessingResult:
    """Result from processing a message"""
    success: bool
    response: str
    model_used: str
    execution_time: float
    tools_used: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None


class AgentCoreV2:
    """
    Unified Agent Core - The Brain (v2.0 Refactored)

    This class orchestrates all AI operations regardless of which interface
    the user is using. Telegram, Web, Slack, or API - all call this same core.

    Key Features:
    - Interface-agnostic processing
    - Dependency injection for testability
    - Event emission for real-time feedback
    - Context-aware conversation handling
    - Structured logging with trace IDs
    """

    def __init__(
        self,
        model_registry: ModelRegistry,
        router: IntelligentRouter,
        execution_engine: ExecutionEngine,
        context_manager: ContextManager,
        event_bus: EventBus,
        prompt_manager: PromptManager,
        config: Dict[str, Any]
    ):
        """
        Initialize the unified core with dependency injection

        Args:
            model_registry: Registry of available models
            router: Intelligent routing system
            execution_engine: Execution engine with backends
            context_manager: Conversation context manager
            event_bus: Event bus for async feedback
            prompt_manager: System prompt manager
            config: Configuration dictionary
        """
        self.config = config
        self.start_time = datetime.now()

        # Injected dependencies (makes testing easy!)
        self.model_registry = model_registry
        self.router = router
        self.execution_engine = execution_engine
        self.context_manager = context_manager
        self.event_bus = event_bus
        self.prompt_manager = prompt_manager

        # Event emitter helper
        self.events = EventEmitter(self.event_bus)

        # Tool registry (reuse existing)
        self.tool_registry = tool_registry
        loaded, failed = self.tool_registry.discover_and_load()

        # Statistics tracking
        self.stats = {
            'messages_processed': 0,
            'total_execution_time': 0.0,
            'tools_executed': 0,
            'by_interface': {},
            'errors': 0
        }

        logger.info(
            "AgentCore v2.0 initialized successfully",
            routing_strategy=router.strategy.value if hasattr(router, 'strategy') else 'unknown',
            tools_loaded=loaded,
            tools_failed=failed,
            models_available=len(model_registry.models)
        )

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
            message: The user's message text (already sanitized by SecurityMiddleware)
            interface: Source interface ("telegram", "web", "slack", etc.)
            user_context: Optional context about the user/session
            files: Optional list of attached files

        Returns:
            ProcessingResult with response and metadata

        Raises:
            PocketPortalError: On processing failures
        """
        start_time = datetime.now()
        user_context = user_context or {}

        # Create trace context for this request
        with TraceContext() as trace_id:
            try:
                # Update statistics
                self.stats['messages_processed'] += 1
                if interface not in self.stats['by_interface']:
                    self.stats['by_interface'][interface] = 0
                self.stats['by_interface'][interface] += 1

                logger.info(
                    "Processing message",
                    chat_id=chat_id,
                    interface=interface,
                    message_length=len(message)
                )

                # Emit processing started event
                await self.events.emit_processing_started(chat_id, message, trace_id)

                # Step 1: Load conversation context
                await self._load_context(chat_id, trace_id)

                # Step 2: Save user message IMMEDIATELY (before processing)
                # This ensures we don't lose the user's message if processing crashes
                await self._save_user_message(chat_id, message, interface)

                # Step 3: Build system prompt from templates
                system_prompt = self._build_system_prompt(interface, user_context)

                # Step 4: Get available tools
                available_tools = [t.metadata.name for t in self.tool_registry.get_all_tools()]

                # Step 5: Route and execute with LLM
                result = await self._execute_with_routing(
                    query=message,
                    system_prompt=system_prompt,
                    available_tools=available_tools,
                    chat_id=chat_id,
                    trace_id=trace_id
                )

                # Step 6: Save assistant response (after successful generation)
                await self._save_assistant_response(chat_id, result.content, interface)

                # Track execution time
                execution_time = (datetime.now() - start_time).total_seconds()
                self.stats['total_execution_time'] += execution_time

                # Extract tools used
                tools_used = getattr(result, 'tools_used', [])
                self.stats['tools_executed'] += len(tools_used)

                logger.info(
                    "Completed processing",
                    model=result.model_id,
                    execution_time=execution_time,
                    tools_count=len(tools_used)
                )

                # Emit completion event
                await self.event_bus.publish(
                    EventType.PROCESSING_COMPLETED,
                    chat_id,
                    {
                        'model': result.model_id,
                        'execution_time': execution_time,
                        'tools_used': tools_used
                    },
                    trace_id
                )

                return ProcessingResult(
                    success=result.success,
                    response=result.content,
                    model_used=result.model_id,
                    execution_time=execution_time,
                    tools_used=tools_used,
                    warnings=[],
                    metadata={
                        'chat_id': chat_id,
                        'interface': interface,
                        'timestamp': start_time.isoformat(),
                        'routing_strategy': self.router.strategy.value if hasattr(self.router, 'strategy') else 'auto'
                    },
                    trace_id=trace_id
                )

            except PocketPortalError as e:
                # Known error - log and rethrow
                self.stats['errors'] += 1
                execution_time = (datetime.now() - start_time).total_seconds()

                logger.error(
                    "Processing failed",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    details=e.details
                )

                await self.event_bus.publish(
                    EventType.PROCESSING_FAILED,
                    chat_id,
                    {'error': e.to_dict()},
                    trace_id
                )

                raise

            except Exception as e:
                # Unknown error - log and wrap
                self.stats['errors'] += 1
                execution_time = (datetime.now() - start_time).total_seconds()

                logger.error(
                    "Unexpected error",
                    error=str(e),
                    exc_info=True
                )

                await self.event_bus.publish(
                    EventType.PROCESSING_FAILED,
                    chat_id,
                    {'error': str(e)},
                    trace_id
                )

                raise PocketPortalError(
                    f"Unexpected error: {str(e)}",
                    details={'original_error': str(e)}
                )

    async def _load_context(self, chat_id: str, trace_id: str):
        """Load conversation context"""
        history = self.context_manager.get_history(chat_id, limit=10)

        await self.event_bus.publish(
            EventType.CONTEXT_LOADED,
            chat_id,
            {'messages_loaded': len(history)},
            trace_id
        )

        logger.debug("Context loaded", chat_id=chat_id, message_count=len(history))

    async def _save_user_message(self, chat_id: str, message: str, interface: str):
        """
        Save user message to context immediately upon receipt

        This ensures we don't lose the user's message if processing crashes.
        """
        self.context_manager.add_message(
            chat_id=chat_id,
            role='user',
            content=message,
            interface=interface
        )
        logger.debug("User message saved", chat_id=chat_id)

    async def _save_assistant_response(self, chat_id: str, response: str, interface: str):
        """
        Save assistant response to context after generation

        Called after successful response generation.
        """
        self.context_manager.add_message(
            chat_id=chat_id,
            role='assistant',
            content=response,
            interface=interface
        )
        logger.debug("Assistant response saved", chat_id=chat_id)

    def _build_system_prompt(self, interface: str, user_context: Optional[Dict]) -> str:
        """
        Build system prompt from external templates

        No more hardcoded strings!
        """
        user_prefs = user_context.get('preferences', {}) if user_context else {}

        return self.prompt_manager.build_system_prompt(
            interface=interface,
            user_preferences=user_prefs
        )

    async def _execute_with_routing(
        self,
        query: str,
        system_prompt: str,
        available_tools: List[str],
        chat_id: str,
        trace_id: str
    ):
        """Execute with intelligent routing"""
        # Get routing decision
        decision = self.router.route(query)

        # Emit routing decision event
        await self.event_bus.publish(
            EventType.ROUTING_DECISION,
            chat_id,
            {
                'model': decision.model_id,
                'reasoning': decision.reasoning,
                'complexity': decision.classification.complexity.value
            },
            trace_id
        )

        logger.info(
            "Routing decision",
            model=decision.model_id,
            complexity=decision.classification.complexity.value
        )

        # Execute with execution engine
        await self.event_bus.publish(
            EventType.MODEL_GENERATING,
            chat_id,
            {'model': decision.model_id},
            trace_id
        )

        result = await self.execution_engine.execute(
            query=query,
            system_prompt=system_prompt,
            available_tools=available_tools
        )

        if not result.success:
            raise ModelNotAvailableError(
                f"Model execution failed: {result.error}",
                details={'model': decision.model_id, 'error': result.error}
            )

        return result

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
            raise ToolExecutionError(
                tool_name,
                f'Tool not found: {tool_name}'
            )

        try:
            result = await tool.execute(parameters)
            return result
        except Exception as e:
            logger.error("Tool execution error", tool=tool_name, error=str(e))
            raise ToolExecutionError(
                tool_name,
                str(e),
                details={'parameters': parameters}
            )

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up AgentCore...")
        await self.execution_engine.cleanup()
        logger.info("AgentCore cleanup complete")


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_agent_core(config: Dict[str, Any]) -> AgentCoreV2:
    """
    Factory function to create AgentCore with all dependencies

    This is the recommended way to instantiate AgentCore.

    Args:
        config: Configuration dictionary

    Returns:
        Initialized AgentCoreV2 instance
    """
    # Initialize all dependencies
    model_registry = ModelRegistry()

    strategy_name = config.get('routing_strategy', 'AUTO').upper()
    routing_strategy = getattr(RoutingStrategy, strategy_name, RoutingStrategy.AUTO)

    router = IntelligentRouter(
        model_registry,
        strategy=routing_strategy,
        model_preferences=config.get('model_preferences', {})
    )

    backend_config = {
        'ollama_base_url': config.get('ollama_base_url', 'http://localhost:11434'),
        'lmstudio_base_url': config.get('lmstudio_base_url', 'http://localhost:1234/v1')
    }

    execution_engine = ExecutionEngine(
        model_registry,
        router,
        backend_config
    )

    context_manager = ContextManager(
        max_context_messages=config.get('max_context_messages', 50)
    )

    event_bus = EventBus()

    prompt_manager = PromptManager()

    # Create and return AgentCore
    return AgentCoreV2(
        model_registry=model_registry,
        router=router,
        execution_engine=execution_engine,
        context_manager=context_manager,
        event_bus=event_bus,
        prompt_manager=prompt_manager,
        config=config
    )
