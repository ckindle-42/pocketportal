# 🚀 PocketPortal 4.1 - Truly Modular AI Agent Platform

**Privacy-First, Interface-Agnostic AI Agent**

---

## 🎉 PocketPortal 4.1 - Production-Ready Modular Architecture

**PocketPortal 4.1** is a refined, production-ready architecture that makes the core **truly interface-agnostic** with a clean, consolidated package structure.

### What's Different in 4.0?

```
Before (3.x):  Telegram Bot → [Monolithic Logic]
After (4.0):   Any Interface → Security → AgentCore → Router → LLM
```

**Key Improvements:**
- ✅ **Modular Architecture**: Add Web/Slack/Discord/API interfaces easily
- ✅ **Dependency Injection**: Fully testable without loading LLMs
- ✅ **Structured Errors**: Custom exceptions instead of string returns
- ✅ **SQLite Rate Limiting**: No more JSON race conditions
- ✅ **Context Management**: Shared conversation history across all interfaces
- ✅ **Event Bus**: Real-time feedback (show spinners, progress indicators)
- ✅ **Structured Logging**: JSON logs with trace IDs for debugging
- ✅ **Externalized Prompts**: Change prompts without redeploying

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
├── pocketportal/                  # 4.1 Unified Package (14,795 lines)
│   ├── core/                      # Agent engine, context, events
│   ├── interfaces/                # Telegram, Web, API interfaces
│   ├── routing/                   # Intelligent model routing
│   ├── security/                  # Security middleware & rate limiting
│   ├── tools/                     # Tool framework (16 categories)
│   │   ├── mcp_tools/            # Model Context Protocol integration
│   │   ├── knowledge/            # Semantic search & knowledge base
│   │   ├── document_processing/  # Office docs, PDFs, Pandoc
│   │   ├── audio_tools/          # Whisper transcription
│   │   ├── automation_tools/     # Scheduling, shell execution
│   │   ├── docker_tools/         # Container management
│   │   └── ... (10 more)
│   ├── config/                    # Configuration management
│   ├── utils/                     # Shared utilities
│   └── __init__.py               # Package exports & version
│
├── tests/                         # Test suite
├── scripts/                       # Setup & utility scripts
│   ├── install.sh                # Complete installation script
│   ├── setup.sh                  # Quick setup script
│   └── deployment/               # Platform-specific deployment configs
│       ├── macos/                # macOS LaunchAgent
│       └── linux/                # Linux systemd service
├── docs/                          # Documentation
│   ├── architecture.md           # Architecture documentation
│   ├── setup.md                  # Installation guide
│   ├── security/                 # Security documentation
│   ├── reports/                  # Verification reports
│   └── archive/                  # Legacy migration guides
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

## 🆕 What's New in 4.1

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

**To migrate to 4.1**: See [`docs/archive/MIGRATION_TO_4.0.md`](docs/archive/MIGRATION_TO_4.0.md)

---

**Version:** 4.1.0
**Release Date:** December 2025
**License:** MIT

**Built with ❤️ for privacy, modularity, and control**
