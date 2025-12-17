# PocketPortal Archive

This directory contains legacy code and documentation from previous iterations of PocketPortal.

## Contents

### `/phase2/` - Phase 2 Architecture
Contains the Phase 2 iteration of PocketPortal with experimental features:
- REST API interface
- Slack bot interface
- Cloud LLM backends
- Old persistent memory implementation

**Status:** Superseded by 4.0 architecture

### `/enhancements/` - Phase 2.5 Enhancements
Contains Phase 2.5 experimental enhancements:
- SQLite-based knowledge base
- Docker Python sandbox
- Enhanced Telegram UI with inline keyboards

**Status:** Not integrated into 4.0

### `/v3_monolithic/` - Version 3.x Monolithic Agent
Contains the monolithic v3.x Telegram agent (`telegram_agent_v3.py`):
- ~800 lines of code
- Monolithic architecture
- Telegram-specific implementation

**Status:** Replaced by modular 4.0 architecture in `pocketportal_unified/`

### `/v3_docs/` - Version 3.x Documentation
Complete v3.x documentation including:
- Deployment guides (DEPLOYMENT_GUIDE_MASTER.md, DEPLOYMENT_GUIDE_MASTER_V3.1.md)
- Part-by-part implementation guides (PART_1 through PART_7)
- Implementation and troubleshooting guides
- Tool addon master plans

**Status:** Archived for reference

### `/legacy_core/` - Legacy Core Files
Contains deprecated core files:
- `agent_engine.py` - Original agent engine (superseded by `agent_engine_v2.py`)

**Status:** Kept for historical reference

## Migration to 4.0

If you're upgrading from v3.x, see the main migration guide:
- **Migration Guide:** `/MIGRATION_TO_4.0.md`
- **4.0 Documentation:** `/pocketportal_unified/README_4.0.md`

## Why Archive These Files?

PocketPortal 4.0 represents a complete architectural refactor focused on:
- **Modularity:** Interface-agnostic core
- **Testability:** Dependency injection throughout
- **Maintainability:** Clean separation of concerns
- **Extensibility:** Easy to add new interfaces

The archived code represents valuable development history but is no longer needed for the 4.0 build.

## Need v3.x?

If you need to reference or run v3.x code:
1. Check the archived files in this directory
2. Review the v3.x documentation in `/v3_docs/`
3. Note that v3.x is no longer actively maintained

---

**Archive Created:** December 2025
**Reason:** 4.0 modular refactor cleanup
