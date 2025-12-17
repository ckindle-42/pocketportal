"""
PocketPortal 4.0 - Unified AI Agent Platform
=============================================

A modular, production-ready AI agent platform with multiple interface support.

Architecture:
    Interface → Security → Core → Router → LLM
                            ├─ Context
                            ├─ Events
                            └─ Prompts

Key Features:
- 🎯 Intelligent routing with model selection
- 🔒 Security middleware with rate limiting
- 🌐 Multiple interfaces (Telegram, Web, API)
- 🧠 Context-aware conversations
- 📊 Structured logging with trace IDs
- 🔧 Extensible tool system
- ⚡ Event-driven architecture

Usage:
    from pocketportal.core import create_agent_core, SecurityMiddleware
    from pocketportal.interfaces import TelegramInterface, WebInterface

    # Create the agent core
    agent = create_agent_core(config)

    # Wrap with security
    secure_agent = SecurityMiddleware(agent)

    # Start interfaces
    telegram = TelegramInterface(secure_agent, config)
    web = WebInterface(secure_agent, config)
"""

__version__ = '4.0.0'
__author__ = 'PocketPortal Team'

# Core components
from .core import (
    AgentCoreV2,
    create_agent_core,
    ProcessingResult,
    ContextManager,
    EventBus,
    EventType,
    SecurityMiddleware,
)

# Routing system
from .routing import (
    IntelligentRouter,
    ModelRegistry,
    ExecutionEngine,
    RoutingStrategy,
)

# Exceptions
from .core.exceptions import (
    PocketPortalError,
    PolicyViolationError,
    ModelNotAvailableError,
    ToolExecutionError,
    RateLimitError,
)

__all__ = [
    # Version
    '__version__',

    # Core
    'AgentCoreV2',
    'create_agent_core',
    'ProcessingResult',
    'ContextManager',
    'EventBus',
    'EventType',
    'SecurityMiddleware',

    # Routing
    'IntelligentRouter',
    'ModelRegistry',
    'ExecutionEngine',
    'RoutingStrategy',

    # Exceptions
    'PocketPortalError',
    'PolicyViolationError',
    'ModelNotAvailableError',
    'ToolExecutionError',
    'RateLimitError',
]
