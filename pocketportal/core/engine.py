"""
Unified Agent Core - Refactored with Dependency Injection
==========================================================

This is the heart of PocketPortal - truly modular and production-ready.

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
import time
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

# Import new unified components
from .context_manager import ContextManager
from .event_bus import EventBus, EventType, EventEmitter
from .prompt_manager import PromptManager
from .structured_logger import get_logger, TraceContext
from .types import InterfaceType
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
    Unified Agent Core - The Brain

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
        tool_registry: 'ToolRegistry',
        config: Dict[str, Any],
        confirmation_middleware: Optional['ToolConfirmationMiddleware'] = None
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
            tool_registry: Registry of available tools
            config: Configuration dictionary
            confirmation_middleware: Optional middleware for human-in-the-loop confirmations
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
        self.tool_registry = tool_registry
        self.confirmation_middleware = confirmation_middleware

        # Event emitter helper
        self.events = EventEmitter(self.event_bus)

        # Load tools from registry
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
            "AgentCore initialized successfully",
            routing_strategy=router.strategy.value if hasattr(router, 'strategy') else 'unknown',
            tools_loaded=loaded,
            tools_failed=failed,
            models_available=len(model_registry.models),
            confirmation_middleware_enabled=confirmation_middleware is not None
        )

    async def process_message(
        self,
        chat_id: str,
        message: str,
        interface: InterfaceType = InterfaceType.UNKNOWN,
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
            interface: Source interface (InterfaceType enum)
            user_context: Optional context about the user/session
            files: Optional list of attached files

        Returns:
            ProcessingResult with response and metadata

        Raises:
            PocketPortalError: On processing failures
        """
        start_time = time.perf_counter()
        user_context = user_context or {}

        # Create trace context for this request
        with TraceContext() as trace_id:
            try:
                # Update statistics
                self.stats['messages_processed'] += 1
                interface_key = interface.value
                if interface_key not in self.stats['by_interface']:
                    self.stats['by_interface'][interface_key] = 0
                self.stats['by_interface'][interface_key] += 1

                logger.info(
                    "Processing message",
                    chat_id=chat_id,
                    interface=interface.value,
                    message_length=len(message)
                )

                # Emit processing started event
                await self.events.emit_processing_started(chat_id, message, trace_id)

                # Step 1: Load conversation context
                await self._load_context(chat_id, trace_id)

                # Step 2: Save user message IMMEDIATELY (before processing)
                # This ensures we don't lose the user's message if processing crashes
                await self._save_user_message(chat_id, message, interface.value)

                # Step 3: Build system prompt from templates
                system_prompt = self._build_system_prompt(interface.value, user_context)

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
                await self._save_assistant_response(chat_id, result.content, interface.value)

                # Track execution time
                execution_time = time.perf_counter() - start_time
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
                        'interface': interface.value,
                        'timestamp': datetime.now().isoformat(),
                        'routing_strategy': self.router.strategy.value if hasattr(self.router, 'strategy') else 'auto'
                    },
                    trace_id=trace_id
                )

            except PocketPortalError as e:
                # Known error - log and rethrow
                self.stats['errors'] += 1
                execution_time = time.perf_counter() - start_time

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
                execution_time = time.perf_counter() - start_time

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

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the agent core and its dependencies

        This method verifies that all critical components are operational:
        - EventBus is active and can publish events
        - ExecutionEngine backends are reachable
        - Model registry has available models
        - Context manager is operational

        Returns:
            Dictionary with health status:
            {
                'status': 'healthy' | 'degraded' | 'unhealthy',
                'timestamp': ISO timestamp,
                'components': {
                    'event_bus': {'status': ..., 'details': ...},
                    'execution_engine': {'status': ..., 'details': ...},
                    'model_registry': {'status': ..., 'details': ...},
                    'context_manager': {'status': ..., 'details': ...},
                    'tool_registry': {'status': ..., 'details': ...}
                },
                'details': {...}
            }

        Note: This is critical for systemd service and Docker health checks
        """
        health_result = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'details': {}
        }

        component_statuses = []

        # Check 1: EventBus
        try:
            # Verify EventBus can publish (test with a dummy event)
            test_event_published = False

            def test_callback(event):
                nonlocal test_event_published
                test_event_published = True

            # Subscribe temporarily, publish test event, then check
            self.event_bus.subscribe(EventType.PROCESSING_STARTED, test_callback)
            await self.event_bus.publish(
                EventType.PROCESSING_STARTED,
                'health_check',
                {'test': True},
                'health_check_trace'
            )

            # Give a moment for async delivery
            await asyncio.sleep(0.01)

            health_result['components']['event_bus'] = {
                'status': 'healthy' if test_event_published else 'degraded',
                'details': {
                    'subscribers': len(self.event_bus._subscribers),
                    'event_history_size': len(self.event_bus._event_history)
                }
            }
            component_statuses.append('healthy' if test_event_published else 'degraded')
        except Exception as e:
            health_result['components']['event_bus'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            component_statuses.append('unhealthy')

        # Check 2: ExecutionEngine / Backends
        try:
            backends_status = {}
            available_backends = 0
            total_backends = len(self.execution_engine.backends)

            for backend_name, backend in self.execution_engine.backends.items():
                try:
                    is_available = await backend.is_available()
                    backends_status[backend_name] = 'available' if is_available else 'unavailable'
                    if is_available:
                        available_backends += 1
                except Exception as e:
                    backends_status[backend_name] = f'error: {str(e)}'

            # Determine health based on backend availability
            if available_backends == 0:
                backend_health = 'unhealthy'
            elif available_backends < total_backends:
                backend_health = 'degraded'
            else:
                backend_health = 'healthy'

            health_result['components']['execution_engine'] = {
                'status': backend_health,
                'details': {
                    'backends': backends_status,
                    'available': available_backends,
                    'total': total_backends,
                    'circuit_breaker_states': {
                        backend_name: self.execution_engine.circuit_breaker.get_state(backend_name).value
                        for backend_name in self.execution_engine.backends.keys()
                    }
                }
            }
            component_statuses.append(backend_health)
        except Exception as e:
            health_result['components']['execution_engine'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            component_statuses.append('unhealthy')

        # Check 3: Model Registry
        try:
            models_count = len(self.model_registry.models)
            health_result['components']['model_registry'] = {
                'status': 'healthy' if models_count > 0 else 'unhealthy',
                'details': {
                    'models_registered': models_count,
                    'models': [model.model_id for model in self.model_registry.models.values()]
                }
            }
            component_statuses.append('healthy' if models_count > 0 else 'unhealthy')
        except Exception as e:
            health_result['components']['model_registry'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            component_statuses.append('unhealthy')

        # Check 4: Context Manager
        try:
            # Basic check that context manager is initialized
            # Try to get context for a test chat_id (won't create if doesn't exist)
            test_context = self.context_manager.get_history('health_check_test', limit=1)
            health_result['components']['context_manager'] = {
                'status': 'healthy',
                'details': {
                    'active_contexts': len(self.context_manager.contexts)
                }
            }
            component_statuses.append('healthy')
        except Exception as e:
            health_result['components']['context_manager'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            component_statuses.append('unhealthy')

        # Check 5: Tool Registry
        try:
            all_tools = self.tool_registry.get_all_tools()
            tools_count = len(all_tools)
            health_result['components']['tool_registry'] = {
                'status': 'healthy' if tools_count > 0 else 'degraded',
                'details': {
                    'tools_loaded': tools_count,
                    'tools': [tool.metadata.name for tool in all_tools[:10]]  # First 10
                }
            }
            component_statuses.append('healthy' if tools_count > 0 else 'degraded')
        except Exception as e:
            health_result['components']['tool_registry'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            component_statuses.append('unhealthy')

        # Determine overall status
        if 'unhealthy' in component_statuses:
            health_result['status'] = 'unhealthy'
        elif 'degraded' in component_statuses:
            health_result['status'] = 'degraded'
        else:
            health_result['status'] = 'healthy'

        # Add summary details
        health_result['details'] = {
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'messages_processed': self.stats['messages_processed'],
            'confirmation_middleware_enabled': self.confirmation_middleware is not None
        }

        logger.info(
            "Health check completed",
            status=health_result['status'],
            components=len(health_result['components'])
        )

        return health_result

    def get_tool_list(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return self.tool_registry.get_tool_list()

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        chat_id: Optional[str] = None,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific tool directly

        This is useful for direct tool execution without LLM reasoning.
        If the tool requires confirmation and confirmation middleware is enabled,
        this method will request approval before executing.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            chat_id: Optional chat ID for confirmation context
            user_id: Optional user ID for confirmation context
            trace_id: Optional trace ID for logging

        Returns:
            Tool execution result

        Raises:
            ToolExecutionError: If tool not found, confirmation denied, or execution fails
        """
        tool = self.tool_registry.get_tool(tool_name)

        if not tool:
            raise ToolExecutionError(
                tool_name,
                f'Tool not found: {tool_name}'
            )

        # Check if tool requires confirmation
        requires_confirmation = getattr(tool.metadata, 'requires_confirmation', False)

        if requires_confirmation and self.confirmation_middleware:
            logger.info(
                f"Tool {tool_name} requires confirmation, requesting approval...",
                tool=tool_name,
                chat_id=chat_id
            )

            # Request confirmation (this will block until approved/denied/timeout)
            approved = await self.confirmation_middleware.request_confirmation(
                tool_name=tool_name,
                parameters=parameters,
                chat_id=chat_id or "unknown",
                user_id=user_id,
                trace_id=trace_id
            )

            if not approved:
                logger.warning(
                    f"Tool execution denied: {tool_name}",
                    tool=tool_name,
                    chat_id=chat_id
                )
                raise ToolExecutionError(
                    tool_name,
                    "Tool execution denied by administrator",
                    details={'parameters': parameters, 'requires_confirmation': True}
                )

            logger.info(
                f"Tool execution approved: {tool_name}",
                tool=tool_name,
                chat_id=chat_id
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
    # Import tool registry here to avoid circular dependencies
    from pocketportal.tools import registry as tool_registry

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
        tool_registry=tool_registry,
        config=config
    )
