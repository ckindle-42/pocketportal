# PocketPortal 4.1 - Project Structure

## Overview

PocketPortal 4.1 has been completely restructured for operational excellence, maintainability, and true modularity. The entire codebase is now contained within a single, self-contained Python package.

## Directory Structure

```
pocketportal/                       # Repository root
├── pocketportal/                   # Main Python package (self-contained)
│   ├── __init__.py                # Package entry point
│   ├── core/                      # The Brain - Core agent logic
│   │   ├── __init__.py
│   │   ├── engine.py              # Main agent orchestration
│   │   ├── context_manager.py     # Conversation history
│   │   ├── event_bus.py           # Real-time event system
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── prompt_manager.py      # External prompt templates
│   │   ├── security_middleware.py # Security wrapper
│   │   └── structured_logger.py   # JSON logging with traces
│   │
│   ├── routing/                   # Intelligent Model Selection
│   │   ├── __init__.py
│   │   ├── intelligent_router.py  # Routing strategies
│   │   ├── task_classifier.py     # Task complexity analysis
│   │   ├── model_registry.py      # Available models catalog
│   │   ├── model_backends.py      # Backend implementations
│   │   ├── execution_engine.py    # LLM execution
│   │   └── response_formatter.py  # Output formatting
│   │
│   ├── security/                  # Security Components
│   │   ├── __init__.py
│   │   ├── security_module.py     # Rate limiting, validation
│   │   ├── sqlite_rate_limiter.py # Persistent rate limits
│   │   └── sandbox/               # Isolated execution
│   │       ├── __init__.py
│   │       └── docker_sandbox.py  # Docker isolation
│   │
│   ├── tools/                     # Extensible Tool System
│   │   ├── __init__.py           # Tool registry
│   │   ├── base_tool.py          # Base tool interface
│   │   ├── system_tools/         # System operations
│   │   ├── git_tools/            # Git integration
│   │   ├── docker_tools/         # Docker management
│   │   ├── web_tools/            # HTTP/web scraping
│   │   ├── data_tools/           # CSV, JSON processing
│   │   ├── audio_tools/          # Whisper transcription
│   │   ├── automation_tools/     # Scheduling, cron
│   │   ├── dev_tools/            # Python environment mgmt
│   │   ├── utilities/            # QR codes, compression, text tools
│   │   ├── mcp_tools/            # Model Context Protocol
│   │   ├── knowledge/            # NEW: Knowledge base
│   │   │   ├── __init__.py
│   │   │   └── knowledge_base_sqlite.py
│   │   └── document_processing/  # NEW: Document suite
│   │       ├── __init__.py
│   │       ├── word_processor.py
│   │       ├── excel_processor.py
│   │       ├── powerpoint_processor.py
│   │       ├── pandoc_converter.py
│   │       └── document_metadata_extractor.py
│   │
│   ├── interfaces/               # User-Facing Adapters
│   │   ├── __init__.py
│   │   ├── telegram_interface.py # Telegram bot
│   │   ├── telegram_ui.py        # Advanced Telegram UI features
│   │   └── web_interface.py      # FastAPI + WebSocket
│   │
│   ├── config/                   # Configuration Management
│   │   ├── __init__.py
│   │   └── (config schemas)
│   │
│   └── utils/                    # Shared Utilities
│       ├── __init__.py
│       └── (helper functions)
│
├── tests/                        # Test suite
│   ├── test_base_tool.py
│   ├── test_security.py
│   ├── test_router.py
│   └── test_data_integrity.py
│
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
# (archive/ removed - legacy code moved to git history)
│
├── pyproject.toml               # Modern Python packaging
├── README.md                    # Main documentation
└── docs/                        # Documentation files
    └── architecture.md          # This file
```

## Key Improvements in 4.1

### 1. **Self-Contained Package**
- Everything lives inside `pocketportal/`
- No external dependencies between directories
- Can be zipped, distributed, and imported cleanly
- Follows modern Python package standards

### 2. **Renamed Components**
- `telegram_agent_tools` → `pocketportal.tools`
  - More generic, works with all interfaces
  - Clearly part of the package
- Tool categories are now subdirectories for better organization

### 3. **Enhanced Tools**
- **Knowledge Base** (`pocketportal.tools.knowledge`)
  - SQLite-based persistent storage
  - Semantic search capabilities
  - From `pocketportal_enhancements`

- **Document Processing** (`pocketportal.tools.document_processing`)
  - Word, Excel, PowerPoint processing
  - Universal document conversion (Pandoc)
  - Metadata extraction
  - From `document_processing_suite`

- **Security Sandbox** (`pocketportal.security.sandbox`)
  - Docker-based code isolation
  - Safe execution environment
  - From `pocketportal_enhancements`

### 4. **Configuration**
- Modern `pyproject.toml` replaces multiple `requirements*.txt`
- Optional dependencies: `pip install pocketportal[all]`
- Or install specific features: `pip install pocketportal[documents,knowledge]`

### 5. **Code Quality Fixes**

**Hardcoded Models Removed**
- `intelligent_router.py` no longer hardcodes model names
- Uses capability-based fallback
- Model preferences loaded from config

**Improved Context Safety**
- User messages saved immediately upon receipt
- Prevents data loss on crash
- Assistant responses saved after generation

**Error Isolation**
- EventBus already wraps listeners in try/except
- One subscriber failure doesn't affect others
- Proper error logging

## Import Changes

### Old (v3.x)
```python
from routing import IntelligentRouter
from telegram_agent_tools import registry
from security.security_module import RateLimiter
```

### New (4.1)
```python
from pocketportal.routing import IntelligentRouter
from pocketportal.tools import registry
from pocketportal.security import RateLimiter
```

## Usage

### Installation

```bash
# Basic installation
pip install -e .

# With all features
pip install -e ".[all]"

# With specific features
pip install -e ".[documents,knowledge,browser]"
```

### Running Interfaces

```python
from pocketportal.core import create_agent_core, SecurityMiddleware
from pocketportal.interfaces import TelegramInterface, WebInterface
from pocketportal.config import load_config

# Load configuration
config = load_config('config.yaml')

# Create the agent core
agent = create_agent_core(config)

# Wrap with security
secure_agent = SecurityMiddleware(agent, config['security'])

# Start interfaces
telegram = TelegramInterface(secure_agent, config)
await telegram.start()

# Or start web interface
web = WebInterface(secure_agent, config)
await web.start()
```

## Migration from v3.x

If you have existing code:

1. **Update imports**: Add `pocketportal.` prefix to all imports
2. **Use `AgentCoreV2`**: Replace `AgentCore` with `AgentCoreV2`
3. **Update config**: Move to `pyproject.toml` format
4. **Update model preferences**: Don't hardcode model names in code

See `MIGRATION_TO_4.0.md` for detailed migration guide.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Interfaces                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Telegram   │  │   Web UI     │  │   Slack      │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                ┌────────────▼────────────┐
                │  Security Middleware   │
                │  • Rate Limiting       │
                │  • Input Validation    │
                │  • Sandboxing          │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │      Agent Core         │
                │  ┌──────────────────┐  │
                │  │  Context Manager │  │
                │  │  Event Bus       │  │
                │  │  Prompt Manager  │  │
                │  └──────────────────┘  │
                └────────────┬────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼─────┐      ┌─────▼──────┐     ┌─────▼─────┐
    │ Routing  │      │   Tools     │     │ Security  │
    │ System   │      │  Registry   │     │  Sandbox  │
    └────┬─────┘      └─────┬──────┘     └─────┬─────┘
         │                  │                   │
    ┌────▼─────┐      ┌─────▼──────┐     ┌─────▼─────┐
    │   LLM    │      │Tool Exec   │     │  Docker   │
    │ Backends │      └────────────┘     │Container  │
    └──────────┘                          └───────────┘
```

## Design Principles

1. **Dependency Injection**: All components receive dependencies, not hardcoded
2. **Interface Segregation**: Core knows nothing about Telegram/Web specifics
3. **Event-Driven**: Real-time feedback via EventBus
4. **Fail-Safe**: Errors isolated, context saved immediately
5. **Configurable**: No hardcoded values, all via config
6. **Testable**: Clean interfaces, easy to mock

## Next Steps

See the roadmap in the main README for planned features:
- Plugin system for dynamic tool loading
- SQLite-based persistent state
- Human-in-the-loop approval middleware
- Process-isolated tool execution
