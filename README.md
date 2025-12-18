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
├── pocketportal/                  # Unified Package
│   ├── core/                      # Agent engine, context, events, job queue
│   ├── interfaces/                # Interface packages
│   │   ├── telegram/             # Telegram bot interface
│   │   │   ├── interface.py      # Main bot logic
│   │   │   └── renderers.py      # UI rendering
│   │   └── web/                  # Web interface
│   │       └── server.py         # FastAPI + WebSocket
│   ├── protocols/                 # Protocol-level integrations
│   │   ├── mcp/                  # Model Context Protocol (bidirectional)
│   │   ├── approval/             # Human-in-the-Loop protocol
│   │   └── resource_resolver.py  # Universal resource access
│   ├── routing/                   # Intelligent model routing
│   ├── security/                  # Security middleware & policies
│   │   ├── middleware.py         # Security middleware
│   │   └── sandbox/              # Docker sandboxing
│   ├── middleware/                # Application middleware
│   │   └── cost_tracker.py       # Cost tracking & business metrics
│   ├── tools/                     # Tool framework
│   │   ├── system_tools/         # System operations
│   │   ├── data_tools/           # CSV, JSON, compression, QR, text
│   │   ├── git_tools/            # Git integration
│   │   ├── web_tools/            # HTTP/web scraping
│   │   ├── media_tools/          # Media processing
│   │   │   └── audio/            # Audio transcription (Whisper)
│   │   ├── automation_tools/     # Scheduling, shell execution
│   │   ├── dev_tools/            # Python environment & session mgmt
│   │   ├── knowledge/            # Semantic search & knowledge base
│   │   └── document_processing/  # PDF OCR, Office docs
│   ├── observability/             # OpenTelemetry, metrics, health
│   ├── persistence/               # DAO pattern repositories
│   ├── config/                    # Configuration & secret management
│   ├── utils/                     # Shared utilities
│   ├── lifecycle.py              # Bootstrap & runtime management
│   └── __init__.py               # Package exports & version
│
├── tests/                         # Test suite
│   ├── unit/                     # Fast unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── scripts/                       # Utility scripts (optional)
├── docs/                          # Documentation
│   ├── architecture.md           # Architecture documentation
│   ├── setup.md                  # Installation guide
│   ├── security/                 # Security documentation
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

## 📚 Legacy v3.x

Previous versions of PocketPortal (v3.x) used a monolithic architecture. Migration documentation has been moved to the `docs/archive/` directory for reference.

**To migrate to 4.x**: See [`docs/archive/MIGRATION_TO_4.0.md`](docs/archive/MIGRATION_TO_4.0.md)

---

**License:** MIT

**Built with ❤️ for privacy, modularity, extensibility, production-readiness, reliability, and architectural excellence**
