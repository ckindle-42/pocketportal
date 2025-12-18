"""
PocketPortal - One-for-All AI Agent Platform
==============================================

A production-ready AI agent platform with plugin architecture, async job queues,
and universal resource access.

Architecture:
    Interface → Security → Core → Router → LLM
                            ├─ Context
                            ├─ Events
                            ├─ Prompts
                            └─ Job Queue

Key Features:
- 🎯 Intelligent routing with model selection
- 🔒 Security middleware with rate limiting
- 🌐 Multiple interfaces (Telegram, Web, API)
- 🧠 Context-aware conversations
- 📊 Structured logging with trace IDs
- 🔧 Extensible tool system with plugin support
- ⚡ Event-driven architecture
- 🔌 Plugin ecosystem via entry_points
- ⏳ Async job queue for heavy workloads
- 🌍 Universal resource access (local, cloud, MCP)
- 📈 OpenTelemetry observability

Usage:
    from pocketportal.core import create_agent_core
    from pocketportal.security import SecurityMiddleware
    from pocketportal.interfaces import TelegramInterface, WebInterface

    # Create the agent core
    agent = create_agent_core(config)

    # Wrap with security
    secure_agent = SecurityMiddleware(agent)

    # Start interfaces
    telegram = TelegramInterface(secure_agent, config)
    web = WebInterface(secure_agent, config)
"""

# Version is dynamically fetched from pyproject.toml (Single Source of Truth)
try:
    from importlib import metadata
    __version__ = metadata.version('pocketportal')
except Exception:
    # Fallback for development environments
    __version__ = '0.0.0-dev'

__author__ = 'PocketPortal Team'

# Core components
from .core import (
    AgentCore,
    create_agent_core,
    ProcessingResult,
    ContextManager,
    EventBus,
    EventType,
)

# Security components
from .security import SecurityMiddleware

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
    'AgentCore',
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
