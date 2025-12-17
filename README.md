# 🚀 PocketPortal 4.0 - Truly Modular AI Agent Platform

**Privacy-First, Interface-Agnostic AI Agent**

---

## 🎉 PocketPortal 4.0 - Complete Modular Architecture

**PocketPortal 4.0** is a complete architectural refactor that makes the core **truly interface-agnostic** and production-ready.

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
# Install dependencies
pip install -r requirements_core.txt

# Run Telegram interface (new architecture)
python pocketportal_unified/interfaces/telegram_interface.py

# Or create your own interface
from pocketportal_unified.core import create_agent_core, SecurityMiddleware
agent_core = create_agent_core(config)
secure_core = SecurityMiddleware(agent_core)
```

### Documentation

📖 **Full 4.0 Documentation**: [`pocketportal_unified/README_4.0.md`](pocketportal_unified/README_4.0.md)
🔄 **Migration from 3.x**: [`MIGRATION_TO_4.0.md`](MIGRATION_TO_4.0.md)
🔧 **Installation Guide**: [`INSTALLATION.md`](INSTALLATION.md)

---

## 📦 Project Structure

```
pocketportal/
├── pocketportal_unified/          # 4.0 Core Architecture
│   ├── core/                      # Agent engine, context, events
│   ├── interfaces/                # Telegram, Web, API interfaces
│   ├── routing/                   # Intelligent model routing
│   ├── tools/                     # Tool framework & registry
│   └── README_4.0.md             # Detailed 4.0 documentation
│
├── routing/                       # Shared routing system
├── security/                      # Security & rate limiting
├── telegram_agent_tools/          # Legacy tool collection (29 tools)
├── tests/                         # Test suite
├── scripts/                       # Setup & utility scripts
├── docs/                          # Current documentation
└── archive/                       # Legacy v3.x code & docs
    ├── phase2/                    # Phase 2 iteration
    ├── enhancements/              # Phase 2.5 enhancements
    ├── v3_monolithic/            # Monolithic v3 agent
    ├── v3_docs/                   # v3.x documentation
    └── legacy_core/               # Old core files
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

**Version:** 4.0.0
**Release Date:** December 2025
**License:** MIT

**Built with ❤️ for privacy, modularity, and control**
