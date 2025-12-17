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
python -m pocketportal.interfaces.telegram_interface

# Or create your own interface
from pocketportal.core import create_agent_core, SecurityMiddleware
agent_core = create_agent_core(config)
secure_core = SecurityMiddleware(agent_core)
```

### Documentation

📖 **Architecture Guide**: [`STRUCTURE.md`](STRUCTURE.md)
🔄 **Migration from 3.x**: [`MIGRATION_TO_4.0.md`](MIGRATION_TO_4.0.md)
🔧 **Installation Guide**: [`INSTALLATION.md`](INSTALLATION.md)
🔒 **Security Enhancements**: [`SECURITY_FIXES.md`](SECURITY_FIXES.md)

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
├── docs/                          # Documentation
├── archive/                       # Legacy v3.x code & docs (reference only)
├── pyproject.toml                 # Modern Python package config
├── STRUCTURE.md                   # Architecture documentation
├── MIGRATION_TO_4.0.md           # Migration guide
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

Your 4.0 deployment succeeds when:
- ✅ Agent responds via Telegram
- ✅ Multiple interfaces work simultaneously
- ✅ Context shared across interfaces
- ✅ Events fire correctly
- ✅ Rate limiting functions
- ✅ No errors in logs

---

## 📚 Legacy v3.x

Previous versions of PocketPortal (v3.x) used a monolithic architecture. All v3.x code and documentation has been moved to the `archive/` directory for reference.

**For v3.x documentation**: See [`archive/v3_docs/`](archive/v3_docs/)
**To migrate to 4.0**: See [`MIGRATION_TO_4.0.md`](MIGRATION_TO_4.0.md)

---

**Version:** 4.1.0
**Release Date:** December 2025
**License:** MIT

**Built with ❤️ for privacy, modularity, and control**
