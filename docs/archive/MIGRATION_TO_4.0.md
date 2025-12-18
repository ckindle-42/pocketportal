# Migration Guide: PocketPortal 3.x → 4.x

This guide helps you migrate from PocketPortal v3.x (monolithic Telegram bot) to v4.x (modular, interface-agnostic architecture).

For a detailed evolution history, see [HISTORY.md](HISTORY.md).
For current architecture documentation, see [docs/architecture.md](../architecture.md).

---

## Table of Contents

1. [Overview](#overview)
2. [Import Changes](#import-changes)
3. [Installation Changes](#installation-changes)
4. [Configuration Changes](#configuration-changes)
5. [Architecture Changes](#architecture-changes)
6. [Breaking Changes Summary](#breaking-changes-summary)
7. [Migration Checklist](#migration-checklist)

---

## Overview

### What Changed?

**v3.x: Monolithic Architecture**
- Single Python script (`telegram_agent_v3.py`)
- Telegram-specific code mixed with core logic
- Manual tool registration
- JSON-based rate limiting (race conditions)
- String-based error returns
- No interface abstraction

**v4.x: Modular Architecture**
- **Core Refactor**: Truly interface-agnostic core
- **Multiple Interfaces**: Telegram, Web, Slack, Discord, API support
- **Dependency Injection**: Fully testable architecture
- **SQLite Rate Limiting**: Thread-safe, transactional
- **Structured Exceptions**: Typed error handling
- **Plugin System**: Dynamic tool discovery and loading

### Key Benefits

- 🔌 **Interface-Agnostic**: Use Telegram, Web, CLI, or build your own
- 🧪 **Testable**: Full dependency injection and mocking support
- 🔐 **Production-Ready**: SQLite, structured logging, error codes
- 🚀 **Extensible**: Plugin architecture for custom tools
- 📦 **Package-Based**: Proper Python package with entry points

---

## Import Changes

### Core Modules

**Old (v3.x)**
```python
from routing import IntelligentRouter
from telegram_agent_tools import registry
from security.security_module import RateLimiter
```

**New (v4.x)**
```python
from pocketportal.routing import IntelligentRouter
from pocketportal.tools import registry
from pocketportal.security import RateLimiter
```

### Tool Development (v4.5.1+)

**Old (v4.0 - v4.5.0)**
```python
from pocketportal.tools.base_tool import BaseTool
from pocketportal.tools.manifest import ToolManifest
```

**New (v4.5.1+)**
```python
from pocketportal.core.interfaces.tool import BaseTool
from pocketportal.core.registries.manifest import ToolManifest
```

### Interface Development (v4.7.3+)

**Old (v4.0 - v4.7.2)**
```python
from pocketportal.interfaces.base import AgentInterface
```

**New (v4.7.3+)**
```python
from pocketportal.core.interfaces.agent_interface import AgentInterface
```

---

## Installation Changes

### v3.x Installation

**Old (v3.x)**
```bash
# Extract tarball
tar -xzf telegram_agent_complete_bundle.tar.gz
cd telegram-agent

# Run setup script
./scripts/setup.sh

# Run directly
python telegram_agent_v3.py
```

### v4.x Installation

**New (v4.x)**
```bash
# Clone repository
git clone https://github.com/ckindle-42/pocketportal.git
cd pocketportal

# Install package (all features)
pip install -e ".[all]"

# Or install with specific extras
pip install -e ".[telegram,web]"  # Only Telegram and Web interfaces

# Use CLI
pocketportal start --interface telegram
```

### Available Installation Profiles

```bash
# Core only (no interfaces, minimal dependencies)
pip install -e .

# Specific interfaces
pip install -e ".[telegram]"     # Telegram bot support
pip install -e ".[web]"          # Web interface support
pip install -e ".[slack]"        # Slack bot support
pip install -e ".[discord]"      # Discord bot support

# Development tools
pip install -e ".[dev]"          # Testing, linting, pre-commit hooks
pip install -e ".[docs]"         # Documentation generation

# Everything (recommended for development)
pip install -e ".[all]"
```

---

## Configuration Changes

### v3.x Configuration

**Old (v3.x)**
- Configuration scattered across multiple files
- Hardcoded model names in code
- Manual tool registration
- No validation

### v4.x Configuration

**New (v4.x)**
- Centralized `config.yaml` or `.env` file
- Model preferences in configuration
- Automatic tool discovery
- Pydantic validation

### Example Configuration

**`.env` (Recommended)**
```bash
# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=claude-3-5-sonnet-20241022

# Interface Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Security
MAX_REQUESTS_PER_MINUTE=10
RATE_LIMIT_WINDOW=60

# Features
ENABLE_MCP_PROTOCOL=true
ENABLE_JOB_QUEUE=true
ENABLE_OBSERVABILITY=false
```

---

## Architecture Changes

### Core Differences

| Aspect | v3.x | v4.x |
|--------|------|------|
| **Structure** | Monolithic script | Modular package |
| **Interfaces** | Telegram only | Multi-interface (Telegram, Web, Slack, Discord, API) |
| **Tool Registration** | Manual | Automatic discovery |
| **Rate Limiting** | JSON file (race conditions) | SQLite (thread-safe) |
| **Error Handling** | String returns | Structured exceptions |
| **Testing** | Difficult | Full DI + mocking |
| **Deployment** | Script execution | Installed package + CLI |

### Package Layout (v4.6.0+)

**Strict src-layout:**
```
pocketportal/
├── src/
│   └── pocketportal/         # Main package (importable)
│       ├── core/             # Agent engine, context, events, job queue
│       ├── interfaces/       # Telegram, Web, Slack, Discord implementations
│       ├── tools/            # Built-in tools (shell, file, browser, etc.)
│       ├── protocols/        # MCP, approval protocol
│       ├── security/         # Authentication, rate limiting
│       ├── routing/          # IntelligentRouter
│       └── config/           # Settings, environment management
├── tests/                    # Test suite (not in package)
├── pyproject.toml            # PEP 517/518 build system
└── README.md
```

**Important:** v4.6.0+ requires package installation. Direct Python file execution no longer works.

---

## Breaking Changes Summary

### v4.0 (Initial Refactor)
- ✅ Complete package restructure
- ✅ All imports require `pocketportal.` prefix
- ✅ `AgentCore` replaces version-specific classes
- ✅ Configuration must use modern format (`.env` or `config.yaml`)

### v4.5.1 (Interface Consolidation)
- ✅ `BaseTool` moved: `from pocketportal.core.interfaces.tool import BaseTool`
- ✅ `ToolManifest` moved: `from pocketportal.core.registries.manifest import ToolManifest`
- ✅ EventBus history opt-in (default: disabled for performance)

### v4.6.0 (Strict src-layout)
- ✅ Strict src-layout: Must install package (`pip install -e .`)
- ✅ Direct Python file execution no longer works
- ✅ Test imports cleaned up (no `sys.path` hacks)
- ✅ Circuit breaker pattern for LLM reliability

### v4.7.3 (Import Path Cleanup)
- ✅ Removed ghost files: `tools/base_tool.py`, `tools/manifest.py`
- ✅ `AgentInterface` moved: `from pocketportal.core.interfaces.agent_interface import AgentInterface`
- ✅ All interfaces and contracts now in `core/interfaces/`

---

## Migration Checklist

### Step 1: Update Environment

```bash
# Uninstall old version (if applicable)
pip uninstall telegram-agent

# Clone v4.x repository
git clone https://github.com/ckindle-42/pocketportal.git
cd pocketportal

# Install with desired extras
pip install -e ".[all]"
```

### Step 2: Update Configuration

```bash
# Create .env file
cp .env.example .env

# Edit with your credentials
nano .env
```

Migrate your old configuration:
- `BOT_TOKEN` → `TELEGRAM_BOT_TOKEN`
- `ALLOWED_USERS` → `TELEGRAM_ALLOWED_USERS`
- `API_KEY` → `ANTHROPIC_API_KEY`
- `MODEL_NAME` → `DEFAULT_MODEL`

### Step 3: Update Custom Code

If you have custom tools or extensions:

1. **Update imports:**
   ```python
   # Old
   from pocketportal.tools.base_tool import BaseTool

   # New
   from pocketportal.core.interfaces.tool import BaseTool
   ```

2. **Ensure proper package structure:**
   - Custom tools in `src/pocketportal/tools/`
   - Custom interfaces in `src/pocketportal/interfaces/`

3. **Update tool registration (if manual):**
   ```python
   # v4.x uses automatic discovery via entry points
   # See pyproject.toml [project.entry-points] for examples
   ```

### Step 4: Run Tests

```bash
# Validate installation
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v           # Unit tests
pytest tests/integration/ -v    # Integration tests
pytest tests/functional/ -v     # End-to-end tests
```

### Step 5: Start the Application

```bash
# Old (v3.x)
python telegram_agent_v3.py

# New (v4.x)
pocketportal start --interface telegram

# Or use specific interface
pocketportal start --interface web --port 8080
```

### Step 6: Verify Functionality

**Validation Checklist:**
- ✅ Bot connects to Telegram successfully
- ✅ Commands respond without errors
- ✅ Tools load and execute correctly
- ✅ Rate limiting works (test with rapid requests)
- ✅ Logs written to correct location
- ✅ Configuration changes take effect

---

## Need Help?

- **Current Architecture**: See [docs/architecture.md](../architecture.md)
- **Installation Guide**: See [docs/setup.md](../setup.md)
- **Changelog**: See [CHANGELOG.md](../../CHANGELOG.md)
- **Evolution History**: See [docs/archive/HISTORY.md](HISTORY.md)
- **GitHub Issues**: [Report a bug or ask questions](https://github.com/ckindle-42/pocketportal/issues)

---

**Version:** 4.7.4
**Last Updated:** 2025-12-18
**License:** MIT
