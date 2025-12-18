# 🚀 PocketPortal - One-for-All AI Agent Platform

**Privacy-First, Interface-Agnostic AI Agent with Professional Architecture and Enterprise Features**

---

## 🎉 Production Reliability & Operational Excellence

**PocketPortal** achieves production-grade reliability with watchdog monitoring, automated log rotation, enhanced graceful shutdown, and refined circuit breaker patterns.

### Key Features

**Core Capabilities:**
- ✅ **Modular Architecture**: Add Web/Slack/Discord/API interfaces easily
- ✅ **Dependency Injection**: Fully testable without loading LLMs
- ✅ **Structured Errors**: Custom exceptions instead of string returns
- ✅ **SQLite Rate Limiting**: No more JSON race conditions
- ✅ **Context Management**: Shared conversation history across all interfaces
- ✅ **Event Bus**: Real-time feedback (show spinners, progress indicators)
- ✅ **Structured Logging**: JSON logs with trace IDs for debugging
- ✅ **Externalized Prompts**: Change prompts without redeploying
- ✅ **DAO Pattern**: Swappable persistence backends (SQLite → PostgreSQL/Redis)
- ✅ **Plugin Architecture**: Third-party tools via entry points
- ✅ **Async Job Queue**: Background processing with priority queue, retries, and worker pools
- ✅ **MCP Protocol Mesh**: Bidirectional MCP support (client + server)
- ✅ **Universal Resources**: Unified access to file://, http://, mcp://, db:// resources
- ✅ **Full Observability**: OpenTelemetry tracing, Prometheus metrics, health probes
- ✅ **Config Hot-Reload**: Zero-downtime configuration updates
- ✅ **Testing Infrastructure**: Organized test markers (unit, integration, slow)
- ✅ **Strict src-layout**: Production-ready package structure (v4.6.0)
- ✅ **Circuit Breaker Pattern**: Backend failure protection with auto-recovery (v4.6.0)
- ✅ **Factory Decoupling**: Clean dependency injection pattern (v4.6.1)
- ✅ **Watchdog System**: Auto-recovery of failed components (v4.7.0)
- ✅ **Log Rotation**: Automated log management with compression (v4.7.0)
- ✅ **Enhanced Graceful Shutdown**: Priority-based shutdown with timeout handling (v4.7.0)

### Quick Start

```bash
# 1. Install core dependencies (required)
pip install -e .

# 2. Verify installation
pocketportal --version
pocketportal validate-config

# 3. (Optional) Install feature-specific dependencies
# See "Dependency Profiles" section below for available extras

# 4. Run your preferred interface
pocketportal start --interface telegram  # or --interface web, or --all

# 5. Validate system health (post-install check)
pocketportal list-tools  # Should show available tools without errors
```

### Dependency Profiles (Optional Extras)

Install only the features you need to minimize dependencies:

```bash
# Basic tool support (QR codes, web scraping)
pip install -e ".[tools]"

# Data processing (pandas, numpy, matplotlib)
pip install -e ".[data]"

# Document processing (Excel, Word, PowerPoint, PDF)
pip install -e ".[documents]"

# Audio transcription (Whisper, pydub)
pip install -e ".[audio]"

# Knowledge base & semantic search (embeddings, FAISS)
pip install -e ".[knowledge]"

# Automation & scheduling (APScheduler, cron)
pip install -e ".[automation]"

# Browser automation (Playwright)
pip install -e ".[browser]"

# Apple Silicon LLM support (MLX framework)
pip install -e ".[mlx]"

# Model Context Protocol support
pip install -e ".[mcp]"

# Production observability (OpenTelemetry, Prometheus)
pip install -e ".[observability]"

# Distributed deployments (Redis event broker)
pip install -e ".[distributed]"

# Docker sandboxing for untrusted code execution
pip install -e ".[security]"

# Development tools (pytest, black, mypy)
pip install -e ".[dev]"

# Everything (all features)
pip install -e ".[all]"
```

**Recommended combinations:**
- **Minimal setup**: Core only (no extras)
- **Personal use**: `pip install -e ".[tools,documents,audio]"`
- **Production deployment**: `pip install -e ".[observability,security,distributed]"`
- **Development**: `pip install -e ".[dev,all]"`

### Post-Install Validation

After installation, verify your setup:

```bash
# Check version and config
pocketportal --version
pocketportal validate-config

# List available tools (should complete without errors)
pocketportal list-tools

# Test health checks (if observability extras installed)
curl http://localhost:8000/health  # Requires web interface running
```

**Expected outcomes:**
- ✅ `pocketportal --version` shows current version from `pyproject.toml`
- ✅ `pocketportal validate-config` reports no errors
- ✅ `pocketportal list-tools` displays tools without import failures
- ✅ No error messages in console output

### Documentation

📖 **Architecture Guide**: [`docs/architecture.md`](docs/architecture.md)
🔄 **Migration from 3.x**: [`docs/archive/MIGRATION_TO_4.0.md`](docs/archive/MIGRATION_TO_4.0.md)
🔧 **Installation Guide**: [`docs/setup.md`](docs/setup.md)
🔒 **Security Enhancements**: [`docs/security/SECURITY_FIXES.md`](docs/security/SECURITY_FIXES.md)

---

## 📦 Project Structure

```
pocketportal/
├── src/                           # Source root (src-layout)
│   └── pocketportal/             # Main package
│       ├── core/                 # Agent engine, context, events, job queue
│       │   ├── interfaces/       # Core contracts and protocols
│       │   └── registries/       # Tool and component registries
│       ├── interfaces/           # Interface implementations
│       │   ├── telegram/         # Telegram bot interface
│       │   └── web/              # Web interface (FastAPI + WebSocket)
│       ├── protocols/            # Protocol-level integrations
│       │   ├── mcp/              # Model Context Protocol (bidirectional)
│       │   ├── approval/         # Human-in-the-Loop protocol
│       │   └── resource_resolver.py  # Universal resource access
│       ├── routing/              # Intelligent model routing
│       ├── security/             # Security middleware & policies
│       │   ├── middleware.py    # Security middleware
│       │   └── sandbox/         # Docker sandboxing
│       ├── middleware/           # Application middleware
│       ├── tools/                # Tool framework
│       │   ├── system_tools/    # System operations
│       │   ├── data_tools/      # CSV, JSON, compression, QR, text
│       │   ├── git_tools/       # Git integration
│       │   ├── web_tools/       # HTTP/web scraping
│       │   ├── media_tools/     # Media processing
│       │   │   └── audio/       # Audio transcription (Whisper)
│       │   ├── automation_tools/ # Scheduling, shell execution
│       │   ├── dev_tools/       # Python environment & session mgmt
│       │   ├── docker_tools/    # Docker operations
│       │   ├── knowledge/       # Semantic search & knowledge base
│       │   ├── document_processing/  # PDF OCR
│       │   └── document_tools/  # Office documents
│       ├── observability/        # OpenTelemetry, metrics, health, watchdog
│       ├── persistence/          # DAO pattern repositories
│       ├── config/               # Configuration & secret management
│       │   └── schemas/         # Pydantic configuration schemas
│       ├── utils/               # Shared utilities
│       ├── lifecycle.py         # Bootstrap & runtime management
│       └── __init__.py          # Package exports & version
│
├── tests/                        # Test suite
│   ├── unit/                    # Fast unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── docs/                         # Documentation
│   ├── architecture.md          # Architecture documentation
│   ├── setup.md                 # Installation guide
│   ├── security/                # Security documentation
│   └── archive/                 # Archived planning documents
├── pyproject.toml                # Modern Python package config (SSOT for version)
├── CHANGELOG.md                  # Version history (SSOT for releases)
└── README.md                     # This file
```

**Note:** This project uses strict src-layout following Python Packaging Authority best practices. The package must be installed (even for development: `pip install -e .`) to enable imports.

---

## 🔐 Security & Privacy

- ✅ 100% local processing
- ✅ Zero cloud API calls
- ✅ SQLite-based rate limiting
- ✅ Input sanitization
- ✅ Encrypted memory storage
- ✅ Structured audit logging

---

## 🎯 Success Criteria

Your deployment succeeds when:
- ✅ Agent responds via Telegram or Web interface
- ✅ Multiple interfaces work simultaneously
- ✅ Context shared across interfaces
- ✅ Events fire correctly
- ✅ Rate limiting functions
- ✅ Configuration validation passes
- ✅ No errors in logs

## 📋 What's New

For detailed release notes and version-specific changes, see [CHANGELOG.md](CHANGELOG.md).

---

## 🔖 Versioning & Release Discipline

PocketPortal follows strict versioning and release governance to ensure credibility and traceability:

### Single Source of Truth (SSOT)

- **`pyproject.toml`** is the authoritative source for the current version number
- All version references are dynamically fetched from `pyproject.toml` via `importlib.metadata`
- Manual version hardcoding is prohibited

### Release Protocol

Every version increment **MUST** include synchronized updates to:

1. **`pyproject.toml`** - Update the `version` field (SSOT)
2. **`CHANGELOG.md`** - Add dated entry with changes (format: `## [X.Y.Z] - YYYY-MM-DD`)
3. **Documentation** - Update any version-specific references if applicable

### Version Numbering (Semantic Versioning)

- **Major.Minor.Patch** (e.g., 4.7.3)
- **Major**: Breaking API changes or architectural redesigns
- **Minor**: New features, backward compatible additions
- **Patch**: Bug fixes, documentation updates, backward compatible improvements

### Release Validation Checklist

Before releasing a new version:

- [ ] Version number updated in `pyproject.toml`
- [ ] `CHANGELOG.md` entry added with actual release date (no placeholders like `YYYY-XX-XX`)
- [ ] All tests passing (`pytest`)
- [ ] Documentation reflects current capabilities
- [ ] Git tag matches version in `pyproject.toml` (e.g., `v4.7.3`)

### Prohibited Practices

- ❌ Future-dated changelog entries
- ❌ Placeholder dates in CHANGELOG (e.g., `2025-XX-XX`)
- ❌ Version bumps without corresponding CHANGELOG entry
- ❌ Hardcoded version numbers in code or documentation

---

## 🧩 Modularity Guide for Contributors

PocketPortal is intentionally designed as a **modular, plugin-based architecture**. Understanding the boundaries between core, extensions, and plugins is critical for safe contributions.

### Architectural Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Interfaces (telegram/, web/)                                │  ← User-facing entry points
├─────────────────────────────────────────────────────────────┤
│ Security Middleware (security/)                             │  ← Rate limiting, auth
├─────────────────────────────────────────────────────────────┤
│ Core (core/)                                                │  ← Agent orchestration
│  ├─ AgentCore: Main processing loop                        │
│  ├─ ContextManager: Conversation state                     │
│  ├─ EventBus: Real-time feedback                           │
│  └─ interfaces/: Contracts & protocols (BaseTool, etc.)    │
├─────────────────────────────────────────────────────────────┤
│ Routing (routing/)                                          │  ← Model selection
├─────────────────────────────────────────────────────────────┤
│ Tools (tools/)                                              │  ← Pluggable capabilities
│  ├─ system_tools/, data_tools/, git_tools/, etc.           │
│  └─ Each tool implements BaseTool interface                │
├─────────────────────────────────────────────────────────────┤
│ Protocols (protocols/)                                      │  ← External integrations
│  ├─ mcp/: Model Context Protocol (bidirectional)           │
│  ├─ approval/: Human-in-the-Loop workflows                 │
│  └─ resource_resolver.py: Universal resource access        │
└─────────────────────────────────────────────────────────────┘
```

### Component Categories

#### 1. **Core** (`core/`, `routing/`, `security/`)
**Purpose:** Orchestration, routing, and security. These are the "central nervous system" of PocketPortal.

**Characteristics:**
- Defines contracts and interfaces (e.g., `BaseTool`, `BaseInterface`)
- Manages conversation context, events, and lifecycle
- Routes requests to appropriate LLM backends
- Enforces security policies

**Contribution Guidelines:**
- ✅ **Safe:** Bug fixes, performance improvements, security patches
- ✅ **Safe:** Adding new events to `EventBus` (non-breaking)
- ✅ **Safe:** New routing strategies (implementing existing interfaces)
- ⚠️ **Caution:** Changing core interfaces (impacts all tools and interfaces)
- ❌ **Avoid:** Breaking changes to `AgentCore`, `ContextManager`, or `EventBus` APIs

#### 2. **Tools** (`tools/`)
**Purpose:** Pluggable capabilities that extend what the agent can do. Tools are **addable and removable without breaking the system**.

**Characteristics:**
- Each tool implements the `BaseTool` interface from `core/interfaces/tool.py`
- Tools are discovered dynamically (no hardcoded registration)
- Tools can be enabled/disabled via configuration
- Tools should be **stateless** (use `ContextManager` for state)

**Contribution Guidelines:**
- ✅ **Encouraged:** New tools in existing categories (e.g., new data processing tools)
- ✅ **Encouraged:** New tool categories (create new subdirectory under `tools/`)
- ✅ **Safe:** Improving existing tools without changing their public interface
- ⚠️ **Caution:** Changing `BaseTool` interface (impacts all tools)
- ❌ **Avoid:** Tools that depend on specific interfaces or create tight coupling

**Example - Adding a New Tool:**
```python
# src/pocketportal/tools/data_tools/csv_analyzer.py
from pocketportal.core.interfaces.tool import BaseTool

class CSVAnalyzerTool(BaseTool):
    name = "csv_analyzer"
    description = "Analyze CSV files and generate statistics"

    async def execute(self, **params):
        # Implementation here
        pass
```

#### 3. **Interfaces** (`interfaces/`)
**Purpose:** User-facing entry points (Telegram, Web, CLI, etc.). Interfaces are **swappable and independent**.

**Characteristics:**
- Each interface implements the `BaseInterface` contract
- Interfaces render responses appropriate to their medium (text, HTML, buttons)
- Interfaces should **not** contain business logic (that belongs in `core/`)

**Contribution Guidelines:**
- ✅ **Encouraged:** New interfaces (Discord, Slack, Voice, etc.)
- ✅ **Safe:** Improving rendering logic within an interface
- ✅ **Safe:** Adding interface-specific features (e.g., Telegram inline keyboards)
- ⚠️ **Caution:** Changes that require core modifications
- ❌ **Avoid:** Duplicating business logic across interfaces

#### 4. **Protocols** (`protocols/`)
**Purpose:** External protocol integrations (MCP, approval workflows, resource resolvers).

**Contribution Guidelines:**
- ✅ **Encouraged:** New protocol integrations (e.g., LSP, DAP)
- ✅ **Safe:** Extending existing protocols (e.g., new MCP providers)
- ⚠️ **Caution:** Changes that impact core architecture

#### 5. **Observability & Middleware** (`observability/`, `middleware/`)
**Purpose:** Cross-cutting concerns (logging, metrics, tracing, cost tracking).

**Contribution Guidelines:**
- ✅ **Safe:** New metrics, new health checks, new log formats
- ✅ **Safe:** New middleware (as long as it's optional)
- ❌ **Avoid:** Mandatory middleware that breaks existing deployments

### Safe Contribution Boundaries

**When adding functionality, ask:**
1. **Can this be a tool?** → Add to `tools/` (preferred)
2. **Is this interface-specific?** → Add to `interfaces/`
3. **Is this a protocol integration?** → Add to `protocols/`
4. **Is this observability?** → Add to `observability/` or `middleware/`
5. **Does this require core changes?** → Discuss in an issue first

### Anti-Patterns to Avoid

- ❌ **God Modules:** Don't create monolithic files with hundreds of lines
- ❌ **Tight Coupling:** Tools should not import from other tools
- ❌ **Interface Leakage:** Don't add Telegram-specific code to `core/`
- ❌ **Breaking Changes:** Don't modify public APIs without major version bump
- ❌ **Hardcoded Dependencies:** Use dependency injection, not `import` statements

### Plugin Development (Advanced)

PocketPortal supports third-party plugins via Python entry points:

```toml
# pyproject.toml for a third-party plugin
[project.entry-points."pocketportal.tools"]
my_custom_tool = "my_plugin.tools:MyCustomTool"
```

Plugins should:
- ✅ Follow the `BaseTool` or `BaseInterface` contracts
- ✅ Be installable via `pip install my-pocketportal-plugin`
- ✅ Work without modifying PocketPortal source code
- ✅ Declare dependencies explicitly in their own `pyproject.toml`

---

## 📚 Legacy v3.x

Previous versions of PocketPortal (v3.x) used a monolithic architecture. Migration documentation has been moved to the `docs/archive/` directory for reference.

**To migrate to 4.x**: See [`docs/archive/MIGRATION_TO_4.0.md`](docs/archive/MIGRATION_TO_4.0.md)

---

**License:** MIT

**Built with ❤️ for privacy, modularity, extensibility, production-readiness, reliability, and architectural excellence**
