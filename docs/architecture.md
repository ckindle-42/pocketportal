# PocketPortal - Architecture Reference

## Overview

PocketPortal represents a significant architectural evolution toward a true "one-for-all" AI agent platform. This document consolidates all architectural decisions, design patterns, and implementation details.

**Note:** For version-specific changes and release history, see [CHANGELOG.md](../CHANGELOG.md) in the root directory.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Recent Improvements (v4.2)](#recent-improvements-v42)
3. [Strategic Vision (v4.3)](#strategic-vision-v43)
4. [Core Architecture](#core-architecture)
5. [Design Principles](#design-principles)

---

## Project Structure

PocketPortal is a self-contained Python package with modular architecture.

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
│   │   ├── system_tools/         # System operations (clipboard, process monitor, stats)
│   │   ├── git_tools/            # Git integration
│   │   ├── docker_tools/         # Docker management
│   │   ├── web_tools/            # HTTP/web scraping
│   │   ├── data_tools/           # CSV, JSON, compression, QR codes, text tools
│   │   ├── audio_tools/          # Whisper transcription
│   │   ├── automation_tools/     # Scheduling, cron
│   │   ├── dev_tools/            # Python environment mgmt
│   │   ├── mcp_tools/            # Model Context Protocol
│   │   ├── knowledge/            # Knowledge base (semantic search, SQLite)
│   │   │   ├── __init__.py
│   │   │   └── knowledge_base_sqlite.py
│   │   └── document_tools/       # Document suite (PDF OCR, Office docs)
│   │       ├── __init__.py
│   │       └── pdf_ocr.py
│   │
│   ├── interfaces/               # User-Facing Adapters
│   │   ├── __init__.py
│   │   ├── telegram_interface.py # Telegram bot
│   │   ├── telegram_renderers.py # Advanced Telegram UI rendering (buttons, menus)
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
2. **Use `AgentCore`**: The unified core class is now simply called `AgentCore`
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

---

## Recent Improvements (v4.2)

This section documents architectural refinements implemented in v4.2.0, focusing on **decoupling**, **scalability**, and **developer experience**.

### 1. Dynamic Tool Discovery (pkgutil-based)

#### Problem
Previously, tools were registered via a hardcoded dictionary in `tools/__init__.py`:
```python
tool_modules = {
    'pocketportal.tools.data_tools.qr_generator': 'QRGeneratorTool',
    'pocketportal.tools.knowledge.local_knowledge': 'LocalKnowledgeTool',
    # ... 16+ hardcoded entries
}
```

**Issues:**
- Required manual updates when adding new tools
- Prone to human error (typos, forgotten entries)
- Not plugin-friendly

#### Solution
Implemented automatic discovery using `pkgutil.walk_packages()`:

```python
# pocketportal/tools/__init__.py
for importer, modname, ispkg in pkgutil.walk_packages([str(tools_dir)], prefix='pocketportal.tools.'):
    module = importlib.import_module(modname)

    # Find all BaseTool subclasses
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseTool) and obj is not BaseTool:
            tool_instance = obj()
            registry.tools[tool_instance.metadata.name] = tool_instance
```

**Benefits:**
- ✅ Zero-config tool registration
- ✅ Automatic discovery of new tools
- ✅ Foundation for external plugin support
- ✅ Reduced maintenance burden

**Files Changed:**
- `pocketportal/tools/__init__.py` (discover_and_load method)

---

### 2. Lazy Loading for Heavy Dependencies

#### Problem
Document processing tools imported heavy libraries at **module level**:
```python
# OLD: pocketportal/tools/document_processing/excel_processor.py
import openpyxl  # ~15MB, loaded even if never used
import pandas as pd  # ~100MB
```

**Issues:**
- Increased startup time (~2-3 seconds for full registry load)
- Wasted memory for unused tools
- Slower CLI responsiveness

#### Solution
Moved all heavy imports inside `execute()` methods (lazy loading):

```python
# NEW: pocketportal/tools/document_processing/excel_processor.py
async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    # Lazy import - only loaded when tool is actually executed
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        return self._error_response("openpyxl not installed")

    # Tool logic here...
```

**Libraries Refactored:**
- `openpyxl` (Excel processing)
- `pandas` (CSV/data analysis)
- `PyPDF2` (PDF extraction)
- `python-docx` (Word processing)
- `python-pptx` (PowerPoint processing)
- `Pillow` (Image metadata)
- `mutagen` (Audio metadata)

**Performance Impact:**
- 📉 **Startup time:** ~3 seconds → <500ms (estimated)
- 📉 **Memory footprint:** ~150MB → ~20MB at startup
- ⚡ **First tool execution:** Slightly slower due to import, but cached afterward

**Files Changed:**
- `pocketportal/tools/document_processing/excel_processor.py`
- `pocketportal/tools/document_processing/document_metadata_extractor.py`

---

### 3. Data Access Object (DAO) Pattern

#### Problem
Core modules (`ContextManager`, `KnowledgeBase`) were **tightly coupled** to SQLite:

```python
# OLD: pocketportal/core/context_manager.py
class ContextManager:
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:  # Hard-coded SQLite
            conn.execute("CREATE TABLE IF NOT EXISTS conversations ...")
```

**Issues:**
- Cannot swap backends (e.g., SQLite → PostgreSQL) without rewriting core logic
- Difficult to test (requires actual database)
- Violates Single Responsibility Principle

#### Solution
Introduced **Repository Pattern** with abstract interfaces:

##### New Architecture

```
pocketportal/persistence/
├── __init__.py              # Public exports
├── repositories.py          # Abstract interfaces
└── sqlite_impl.py           # SQLite implementation
```

##### Abstract Interfaces

```python
# pocketportal/persistence/repositories.py
class ConversationRepository(ABC):
    @abstractmethod
    async def add_message(self, chat_id: str, role: str, content: str) -> None:
        pass

    @abstractmethod
    async def get_messages(self, chat_id: str, limit: int = None) -> List[Message]:
        pass

class KnowledgeRepository(ABC):
    @abstractmethod
    async def add_document(self, content: str, embedding: List[float]) -> str:
        pass

    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Document]:
        pass
```

##### Concrete Implementation

```python
# pocketportal/persistence/sqlite_impl.py
class SQLiteConversationRepository(ConversationRepository):
    # Implements all abstract methods using SQLite

class SQLiteKnowledgeRepository(KnowledgeRepository):
    # Implements all abstract methods using SQLite + FTS5
```

##### Usage (Future)

```python
# Dependency Injection - swap backends via configuration
if config.database_backend == "sqlite":
    conversation_repo = SQLiteConversationRepository(db_path)
elif config.database_backend == "postgresql":
    conversation_repo = PostgreSQLConversationRepository(connection_string)

# Core logic remains unchanged - depends on interface, not implementation
context_manager = ContextManager(repository=conversation_repo)
```

**Benefits:**
- ✅ **Testability:** Mock repositories for unit tests
- ✅ **Flexibility:** Swap SQLite → PostgreSQL with zero core logic changes
- ✅ **Scalability:** Use Redis for sessions, Pinecone for vectors, etc.
- ✅ **Separation of Concerns:** Core logic doesn't care about database details

**Repository Interfaces:**
1. **ConversationRepository**
   - Stores conversation history (messages)
   - Methods: `add_message`, `get_messages`, `search_messages`, `delete_conversation`
   - Implementations: SQLite (current), PostgreSQL (future), Redis (future)

2. **KnowledgeRepository**
   - Stores documents with embeddings
   - Methods: `add_document`, `search`, `search_by_embedding`, `delete_document`
   - Implementations: SQLite+FTS5 (current), PostgreSQL+pgvector (future), Pinecone (future)

**Files Added:**
- `pocketportal/persistence/__init__.py`
- `pocketportal/persistence/repositories.py`
- `pocketportal/persistence/sqlite_impl.py`

---

## Strategic Vision (v4.3)

PocketPortal v4.3 focuses on becoming a true "one-for-all" platform. See `docs/STRATEGIC_PLAN_V4.3.md` for comprehensive details.

**Key Additions:**

### 1. Plugin Architecture (Entry Points)
- Third-party tools via Python entry_points
- `pip install pocketportal-tool-X` auto-discovery
- Community ecosystem enablement

### 2. Async Job Queue
- Non-blocking execution for heavy workloads
- Background processing for video, OCR, large data
- User notifications on completion

### 3. MCP Protocol Elevation
- Move from `tools/mcp_tools` to `protocols/mcp`
- Bidirectional MCP (client and server)
- Universal resource resolver (local, drive, s3, mcp URIs)

### 4. Observability
- OpenTelemetry integration
- Distributed tracing
- Health/readiness endpoints
- Config hot-reloading

**See:** `docs/STRATEGIC_PLAN_V4.3.md` for full implementation details

---

## Next Steps

**Immediate (v4.3.0):**
- ✅ Plugin architecture with entry_points
- ✅ Async job queue for heavy tools
- ✅ MCP protocol layer restructure
- ✅ Observability & health checks

**Future (v4.4+):**
- Stateful execution (Jupyter kernels)
- GraphRAG integration
- Advanced plugin marketplace
