# 🚀 PocketPortal 4.4.0 - One-for-All AI Agent Platform

**Privacy-First, Interface-Agnostic AI Agent with Async Queue, Protocol Mesh, and Full Observability**

---

## 🎉 PocketPortal 4.4.0 - Production-Ready Enterprise Platform

**PocketPortal 4.4.0** is a production-ready, extensible AI agent platform with **async job queues**, **bidirectional MCP support**, **universal resource resolution**, and **full observability** that makes it truly interface-agnostic and production-grade.

### Evolution from 3.x to 4.4.0

```
v3.x:  Telegram Bot → [Monolithic Logic]
v4.0:  Any Interface → Security → AgentCore → Router → LLM
v4.2:  + DAO Pattern + Dynamic Discovery + Lazy Loading
v4.3:  + Plugin Ecosystem + Observability + Testing Infrastructure
v4.4:  + Async Job Queue + MCP Protocol Mesh + Full Observability Stack
```

**Core Improvements (4.0-4.4):**
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

### Quick Start

```bash
# Install core dependencies
pip install -e .

# Or install with all features
pip install -e ".[all]"

# Run Telegram interface
pocketportal start --interface telegram

# Or run all interfaces
pocketportal start --all

# Validate your configuration
pocketportal validate-config

# List available tools
pocketportal list-tools
```

### Documentation

📖 **Architecture Guide**: [`docs/architecture.md`](docs/architecture.md)
🔄 **Migration from 3.x**: [`docs/archive/MIGRATION_TO_4.0.md`](docs/archive/MIGRATION_TO_4.0.md)
🔧 **Installation Guide**: [`docs/setup.md`](docs/setup.md)
🔒 **Security Enhancements**: [`docs/security/SECURITY_FIXES.md`](docs/security/SECURITY_FIXES.md)

---

## 📦 Project Structure

```
pocketportal/
├── pocketportal/                  # 4.1 Unified Package
│   ├── core/                      # Agent engine, context, events
│   ├── interfaces/                # Telegram, Web, API interfaces
│   │   ├── telegram_interface.py # Telegram bot
│   │   ├── telegram_renderers.py # Telegram UI rendering
│   │   └── web_interface.py      # FastAPI + WebSocket
│   ├── routing/                   # Intelligent model routing
│   ├── security/                  # Security middleware & rate limiting
│   ├── tools/                     # Tool framework
│   │   ├── system_tools/         # System operations
│   │   ├── data_tools/           # CSV, JSON, compression, QR, text
│   │   ├── git_tools/            # Git integration
│   │   ├── docker_tools/         # Container management
│   │   ├── web_tools/            # HTTP/web scraping
│   │   ├── audio_tools/          # Whisper transcription
│   │   ├── automation_tools/     # Scheduling, shell execution
│   │   ├── dev_tools/            # Python environment mgmt
│   │   ├── mcp_tools/            # Model Context Protocol
│   │   ├── knowledge/            # Semantic search & knowledge base
│   │   └── document_tools/       # PDF OCR, Office docs
│   ├── config/                    # Configuration management
│   ├── utils/                     # Shared utilities
│   └── __init__.py               # Package exports & version
│
├── tests/                         # Test suite
├── docs/                          # Documentation
│   ├── architecture.md           # Architecture documentation
│   ├── setup.md                  # Installation guide
│   ├── security/                 # Security documentation
│   ├── reports/                  # Verification reports (gitignored)
│   └── archive/                  # Archived planning documents
├── pyproject.toml                 # Modern Python package config
└── README.md                      # This file
```

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

Your 4.1 deployment succeeds when:
- ✅ Agent responds via Telegram or Web interface
- ✅ Multiple interfaces work simultaneously
- ✅ Context shared across interfaces
- ✅ Events fire correctly
- ✅ Rate limiting functions
- ✅ Configuration validation passes
- ✅ No errors in logs

## 🆕 What's New in 4.4

### Phase 2: Async Job Queue
- **Priority Job Queue**: Background processing with LOW/NORMAL/HIGH/CRITICAL priorities
- **Worker Pool**: Concurrent job processing with configurable worker count
- **Auto Retry**: Automatic retry on failure with exponential backoff
- **Event Integration**: Real-time job status updates via event bus
- **Stale Job Recovery**: Automatic detection and requeuing of stuck jobs
- **Swappable Backends**: DAO pattern supports SQLite, Redis, PostgreSQL

### Phase 3: MCP Protocol Elevation
- **Bidirectional MCP**: Run as both MCP client AND server
- **Protocol Mesh**: Connect PocketPortal ↔ Claude Desktop ↔ Other MCP apps
- **Universal Resources**: Unified API for file://, http://, mcp://, db:// resources
- **Resource Providers**: Pluggable providers for different resource types
- **Batch Resolution**: Resolve multiple resources in parallel
- **CLI Server**: `pocketportal mcp-server` to expose tools via MCP

### Phase 4: Full Observability Stack
- **OpenTelemetry Tracing**: Distributed tracing with Jaeger/Tempo integration
- **Prometheus Metrics**: Production-grade metrics at `/metrics` endpoint
  - HTTP request counters and duration histograms
  - Job queue metrics (pending, running, completed)
  - Worker pool metrics (total, busy, idle)
  - LLM request metrics (tokens, duration, model)
  - Error counters by type and component
- **Kubernetes Health Probes**:
  - `/health/live` - Liveness probe
  - `/health/ready` - Readiness probe
  - `/health` - Full health check
- **Config Hot-Reload**: Zero-downtime configuration updates
  - Watch YAML/JSON/TOML config files
  - Automatic validation and rollback
  - Callback system for config changes

### Previous: 4.3 Features
- **Plugin Ecosystem**: Third-party tools via entry points
- **Testing Infrastructure**: pytest markers for organized test execution
- **Documentation**: Consolidated docs and strategic planning

---

## 🔧 What's New in 4.2

### Architectural Refinements
- **DAO Pattern**: Repository interfaces for swappable persistence (SQLite → PostgreSQL/Redis)
- **Dynamic Tool Discovery**: pkgutil-based automatic tool registration (zero manual updates)
- **Lazy Loading**: Heavy dependencies loaded on-demand (startup: ~3s → <500ms)
- **Persistence Layer**: Abstract repositories (`ConversationRepository`, `KnowledgeRepository`)
- **Scalability Foundation**: Core logic decoupled from database implementation

---

## ⚙️ What's New in 4.1

### Operational Excellence
- **Pydantic Settings**: Type-safe configuration with validation at startup
- **BaseInterface ABC**: Standardized interface contract for consistency
- **Dynamic Tool Discovery**: Auto-detect tools without manual registration
- **Unified CLI**: Single `pocketportal` command for all operations
- **Deployment Configs**: Ready-to-use systemd and launchd configurations

### Cleaner Structure
- Consolidated documentation in `docs/` directory
- Platform-specific deployment scripts organized by OS
- Updated installation scripts using modern `pyproject.toml`
- Removed legacy v3.x artifacts and version conflicts

---

## 📚 Legacy v3.x

Previous versions of PocketPortal (v3.x) used a monolithic architecture. Migration documentation has been moved to the `docs/archive/` directory for reference.

**To migrate to 4.x**: See [`docs/archive/MIGRATION_TO_4.0.md`](docs/archive/MIGRATION_TO_4.0.md)

---

**Version:** 4.4.0
**Release Date:** December 2025
**License:** MIT

**Built with ❤️ for privacy, modularity, extensibility, production-readiness, and control**
