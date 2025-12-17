"""
PocketPortal 4.0 - Unified Core Module
======================================

This module contains the core components of PocketPortal 4.0,
refactored for true modularity and operational excellence.

Architecture Overview:
    Interface → SecurityMiddleware → AgentCore → Router → LLM
                                       ├─ ContextManager
                                       ├─ EventBus
                                       └─ PromptManager

Key Improvements in 4.0:
- ✅ Dependency Injection for testability
- ✅ Structured error handling with custom exceptions
- ✅ Unified context management across interfaces
- ✅ Event bus for real-time feedback
- ✅ Structured logging with trace IDs
- ✅ Externalized prompts for easy iteration
- ✅ SQLite-based rate limiting with proper locking
- ✅ Security middleware wrapper

Usage:
    from pocketportal.core import (
        create_agent_core,
        SecurityMiddleware,
        ProcessingResult
    )

    # Create core with factory function
    config = {...}
    agent_core = create_agent_core(config)

    # Wrap with security middleware
    secure_core = SecurityMiddleware(agent_core)

    # Process messages
    result = await secure_core.process_message(
        chat_id="user_123",
        message="Hello!",
        interface="telegram"
    )
"""

# Core engine
from .agent_engine_v2 import AgentCoreV2, ProcessingResult, create_agent_core

# Components
from .context_manager import ContextManager, Message
from .event_bus import EventBus, EventType, Event, EventEmitter
from .prompt_manager import PromptManager, get_prompt_manager
from .security_middleware import SecurityMiddleware, SecurityContext
from .structured_logger import (
    StructuredLogger,
    TraceContext,
    get_logger,
    get_trace_id,
    set_trace_id
)

# Exceptions
from .exceptions import (
    PocketPortalError,
    PolicyViolationError,
    ModelQuotaExceededError,
    ModelNotAvailableError,
    ToolExecutionError,
    AuthorizationError,
    RateLimitError,
    ContextNotFoundError,
    ValidationError
)

__all__ = [
    # Core engine
    'AgentCoreV2',
    'ProcessingResult',
    'create_agent_core',

    # Components
    'ContextManager',
    'Message',
    'EventBus',
    'EventType',
    'Event',
    'EventEmitter',
    'PromptManager',
    'get_prompt_manager',
    'SecurityMiddleware',
    'SecurityContext',

    # Logging
    'StructuredLogger',
    'TraceContext',
    'get_logger',
    'get_trace_id',
    'set_trace_id',

    # Exceptions
    'PocketPortalError',
    'PolicyViolationError',
    'ModelQuotaExceededError',
    'ModelNotAvailableError',
    'ToolExecutionError',
    'AuthorizationError',
    'RateLimitError',
    'ContextNotFoundError',
    'ValidationError',
]

__version__ = '4.0.0'
