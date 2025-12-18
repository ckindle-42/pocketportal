# Changelog

All notable changes to PocketPortal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.7.0] - 2025-12-18

### Added - Production Reliability & Operational Excellence

- **v4.6.1: Factory Decoupling**
  - Extracted dependency creation from `create_agent_core()` into `core/factories.py`
  - New `DependencyContainer` class for managing all AgentCore dependencies
  - Individual factory functions for each component (router, execution engine, etc.)
  - Better testability through dependency injection
  - Easier customization of implementations
  - Cleaner separation of concerns between creation and usage

- **v4.6.2: Circuit Breaker Refinements**
  - Made circuit breaker configurable (can now be disabled if needed)
  - Added `circuit_breaker_enabled` configuration option
  - Enhanced health check integration with circuit breaker state
  - Added `get_circuit_breaker_status()` method for detailed status reporting
  - Safe handling when circuit breaker is disabled
  - Added `cleanup()` method to ExecutionEngine for graceful shutdown
  - Better logging of circuit state changes and failures
  - Configuration options:
    - `circuit_breaker_enabled`: Enable/disable circuit breaker (default: True)
    - `circuit_breaker_threshold`: Failures before opening (default: 3)
    - `circuit_breaker_timeout`: Recovery timeout in seconds (default: 60)
    - `circuit_breaker_half_open_calls`: Test calls in half-open state (default: 1)

- **v4.7.0: Watchdog System** (`observability/watchdog.py`)
  - Process monitoring and auto-recovery system
  - Monitors critical components (workers, interfaces, event broker)
  - Automatic component restart on failure
  - Configurable failure thresholds and restart policies
  - Exponential backoff for restart attempts
  - Resource monitoring (memory, CPU usage)
  - Integration with health check system
  - Component states: HEALTHY, DEGRADED, FAILED, RESTARTING, STOPPED
  - Manual component restart and reset capabilities
  - Configuration options:
    - `watchdog_enabled`: Enable watchdog monitoring (default: False)
    - `watchdog_check_interval_seconds`: Health check interval (default: 30)
    - `watchdog_max_consecutive_failures`: Failures before restart (default: 3)
    - `watchdog_restart_on_failure`: Auto-restart on failure (default: True)

- **v4.7.0: Log Rotation** (`observability/log_rotation.py`)
  - Automated log file rotation with multiple strategies
  - Size-based rotation (default: 10MB per file)
  - Time-based rotation (default: daily)
  - Automatic compression of rotated logs (gzip)
  - Cleanup of old rotated files
  - Async operation for non-blocking I/O
  - Integration with Python's logging system via `RotatingStructuredLogHandler`
  - Configuration options:
    - `log_rotation_enabled`: Enable log rotation (default: True)
    - `log_max_bytes`: Max size before rotation (default: 10MB)
    - `log_rotation_interval_hours`: Time-based rotation (default: 24h)
    - `log_backup_count`: Number of backups to keep (default: 7)
    - `log_compress_rotated`: Compress old logs (default: True)

- **v4.7.0: Enhanced Graceful Shutdown** (updated `lifecycle.py`)
  - Priority-based shutdown sequence
  - Timeout handling for all shutdown operations
  - Task draining (wait for in-flight operations)
  - Stop accepting new work before shutdown
  - Six-phase shutdown process:
    1. Stop accepting new work
    2. Drain in-flight operations
    3. Stop optional components (watchdog, log rotation)
    4. Run priority-ordered shutdown callbacks
    5. Cleanup agent core
    6. Clear event history
  - Per-callback timeout configuration
  - Shutdown priority levels: CRITICAL, HIGH, NORMAL, LOW, LOWEST
  - Active task tracking and monitoring
  - Shutdown duration logging and validation
  - Configuration: `shutdown_timeout_seconds` (default: 30s)

### Changed - Enhanced Configuration & Lifecycle

- **v4.6.1: Simplified create_agent_core()**
  - Reduced from ~50 lines to ~10 lines
  - Now delegates to factory functions for clarity
  - Maintains backward compatibility
  - Example usage documented in docstring

- **v4.6.2: ExecutionEngine Enhancements**
  - Circuit breaker now optional (configurable)
  - Better error handling when circuit breaker is disabled
  - Added comprehensive logging of initialization parameters
  - Fixed settings initialization order

- **v4.7.0: RuntimeContext Enhancements**
  - Added `watchdog` and `log_rotator` fields
  - New `active_tasks` set for tracking in-flight operations
  - New `accepting_work` flag for shutdown coordination
  - Changed `shutdown_callbacks` from List[Callable] to List[ShutdownCallback]

- **v4.7.0: Runtime Class Enhancements**
  - Added `enable_watchdog` and `enable_log_rotation` parameters
  - Added `shutdown_timeout` parameter for configurable grace period
  - New methods:
    - `track_task()`: Track tasks for graceful draining
    - `is_accepting_work()`: Check if system is shutting down
    - `_drain_active_tasks()`: Wait for active tasks to complete
  - Enhanced `register_shutdown_callback()` with priority and timeout

### Configuration Schema Updates

- **LLMConfig** (v4.6.2):
  - Added circuit breaker configuration fields
  - All circuit breaker settings with validation

- **ObservabilityConfig** (v4.7.0):
  - Added log rotation configuration fields
  - Added watchdog configuration fields
  - Comprehensive validation for all new settings

- **SettingsSchema** (v4.7.0):
  - Added `shutdown_timeout_seconds` field

### Technical Improvements

- **Dependency Injection**: Factory pattern for better testability (v4.6.1)
- **Resilience**: Optional circuit breaker with configurable behavior (v4.6.2)
- **Monitoring**: Watchdog system for automatic recovery (v4.7.0)
- **Log Management**: Automated rotation and cleanup (v4.7.0)
- **Graceful Degradation**: Enhanced shutdown with timeouts and draining (v4.7.0)
- **Production Ready**: All features designed for long-running deployments

### Migration Notes

- **v4.6.1 - Non-Breaking**: Factory functions are internal, `create_agent_core()` API unchanged
- **v4.6.2 - Non-Breaking**: Circuit breaker enabled by default, can be disabled via config
- **v4.7.0 - Non-Breaking**: All new features are opt-in via configuration
  - Watchdog: Disabled by default, enable with `watchdog_enabled=True`
  - Log Rotation: Enabled by default, disable with `log_rotation_enabled=False`
  - Enhanced Shutdown: Works automatically, configure timeout if needed

### Performance Impact

- **v4.6.1**: Minimal (factory overhead is one-time during initialization)
- **v4.6.2**: None when circuit breaker is enabled (already present in v4.6.0)
- **v4.7.0**:
  - Watchdog: Minimal (runs async every 30s by default)
  - Log Rotation: Minimal (async background task)
  - Enhanced Shutdown: None during normal operation, better cleanup on exit

## [4.6.0] - 2025-12-18

### Added - Import Safety & Reliability

- **Strict src-layout**: Migrated to `src/pocketportal/` layout following Python packaging best practices
  - Prevents accidental imports from source tree during development
  - Forces proper package installation for all imports
  - Catches import errors early in development cycle
  - Aligns with Python Packaging Authority recommendations
  - Updated `pyproject.toml` with `package-dir = {"" = "src"}`

- **Circuit Breaker Pattern**: Fully implemented in ExecutionEngine for backend resilience
  - Three states: CLOSED (normal), OPEN (failing), HALF_OPEN (testing recovery)
  - Configurable failure threshold (default: 3 failures)
  - Automatic recovery testing after timeout (default: 60 seconds)
  - Per-backend state tracking (Ollama, LMStudio, MLX independently managed)
  - Health check integration showing circuit state and failure counts
  - Manual circuit reset capability via `reset_circuit_breaker(backend_name)`
  - Prevents wasted resources on repeatedly failing backends
  - Improves response times by failing fast when backends are down

### Changed - Package Structure

- **Source Layout Migration**: All package code moved to `src/pocketportal/`
  - Previous: `/pocketportal/` (flat layout)
  - Current: `/src/pocketportal/` (src-layout)
  - Tests remain at `/tests/` (outside src)
  - Better isolation between source and tests

- **Test Import Cleanup**: Removed all `sys.path.insert()` hacks from test files
  - All tests now use proper `from pocketportal` imports
  - Tests properly validate installed package, not source tree
  - Cleaner test code without path manipulation

### Technical Improvements

- Enhanced package hygiene with strict src-layout
- Improved reliability with circuit breaker pattern
- Better failure handling in ExecutionEngine
- Faster failure detection for unavailable backends
- Cleaner test architecture

### Migration Notes

- **Breaking Change**: Package must now be installed to import
  ```bash
  # Development installation required
  pip install -e .
  ```
- **Non-Breaking**: All public APIs remain unchanged
- **Non-Breaking**: Import paths unchanged (still `from pocketportal...`)
- **Non-Breaking**: Circuit breaker is opt-in via configuration:
  ```python
  config = {
      'circuit_breaker_threshold': 3,      # Failures before opening
      'circuit_breaker_timeout': 60,       # Seconds before retry
      'circuit_breaker_half_open_calls': 1 # Test calls in half-open
  }
  ```

## [4.5.1] - 2025-12-18

### Changed - Documentation & Version Integrity
- **Architecture Documentation**: Made `docs/architecture.md` version-agnostic by removing specific version numbers from headers
  - Renamed from "PocketPortal v4.3.0" to "PocketPortal - Architecture Reference"
  - Added reference to CHANGELOG.md as the single source of version history
  - Reduces documentation maintenance debt and prevents version drift

- **README Cleanup**: Moved "What's New" sections to CHANGELOG.md
  - Removed version-specific feature lists from README
  - README now focuses on current state, not historical changes
  - CHANGELOG.md is now the primary source for release notes

- **Root Directory Hygiene**: Removed redundant `__init__.py` from repository root
  - Prevents import confusion between project root and package directory

### Changed - Project Structure & Packaging
- **Tool Interface Refactoring**: Moved `BaseTool` to core contracts
  - Moved `pocketportal/tools/base_tool.py` → `pocketportal/core/interfaces/tool.py`
  - BaseTool is a core contract, not a tool itself
  - Prevents circular imports when Core needs to type-check tools
  - Created new `pocketportal/core/interfaces/` package for core contracts

- **Registry Organization**: Moved `ToolManifest` to core registries
  - Moved `pocketportal/tools/manifest.py` → `pocketportal/core/registries/manifest.py`
  - Created new `pocketportal/core/registries/` package for registration schemas
  - Better separation of concerns: tools vs. tool registration

- **Test Organization**: Moved verification scripts to E2E tests
  - Moved `scripts/verification/*.py` → `tests/e2e/`
  - Added `tests/e2e/README.md` with E2E testing guidelines
  - Formalizes manual verification scripts as automated E2E tests

- **Import Updates**: Updated all 35+ tool files to use new import paths
  - All tools now import from `pocketportal.core.interfaces.tool`
  - All manifests now import from `pocketportal.core.registries.manifest`

### Changed - Core Stability & Error Handling
- **EventBus Memory Management**: Made event history opt-in to prevent memory leaks
  - Changed `EventBus.__init__(enable_history: bool = False, max_history: int = 1000)`
  - Event history now **disabled by default** for long-running agents
  - For production auditing, users should use the persistence layer instead
  - Prevents memory leaks from accumulating events in RAM over weeks/months

- **Structured Error Codes**: Added numeric error codes to all exceptions
  - New `ErrorCode` enum with categorized codes:
    - 1xxx: Client errors (validation, parameters)
    - 2xxx: Security errors (auth, rate limiting)
    - 3xxx: Resource errors (model unavailable, quota)
    - 4xxx: Execution errors (tool execution, processing)
    - 5xxx: System errors (internal, database)
  - All exception subclasses now use error codes
  - Added `PocketPortalError.user_message()` for user-friendly error messages
  - Enables interfaces to show contextual messages (e.g., "Error 503: Model Busy")

### Technical Improvements
- Reduced cognitive load by consolidating documentation
- Improved package hygiene and import paths
- Enhanced error handling for better user experience
- Prevented memory leaks in long-running deployments
- Strengthened architectural boundaries (core vs. tools)

### Migration Notes
- **Breaking Change**: Code importing `BaseTool` must update import path:
  ```python
  # Old
  from pocketportal.tools.base_tool import BaseTool

  # New
  from pocketportal.core.interfaces.tool import BaseTool
  ```
- **Breaking Change**: Code importing `ToolManifest` must update import path:
  ```python
  # Old
  from pocketportal.tools.manifest import ToolManifest

  # New
  from pocketportal.core.registries.manifest import ToolManifest
  ```
- **Breaking Change**: `EventBus` now requires explicit `enable_history=True` to store event history
  ```python
  # Old (history enabled by default)
  event_bus = EventBus()

  # New (history disabled by default)
  event_bus = EventBus(enable_history=True)  # Only if you need history
  ```
- **Non-Breaking**: All exception constructors remain backward compatible
  - Error codes are automatically assigned
  - Existing code continues to work without modification

## [4.5.0] - 2025-12-18

### Added - Project Structure & Hygiene
- **Cleaned Root Directory**: Moved standalone test files to `scripts/verification/`
  - Relocated `test_phase2_standalone.py`, `test_phase3_standalone.py`, `test_phase4_standalone.py`
  - Root directory now only contains configuration files and package source
  - Professional appearance matching the architecture quality

### Added - Architectural Refinements
- **Modular Interfaces**: Converted flat interfaces into sub-packages
  - `interfaces/telegram/`: Telegram bot interface and renderers
  - `interfaces/web/`: FastAPI + WebSocket web interface
  - Co-locates interface-specific assets within their packages
  - Better organization and future-proofing

- **EventBroker Interface**: Abstract interface for event bus implementations (`core/event_broker.py`)
  - `EventBroker` ABC following DAO pattern
  - `MemoryEventBroker` for single-process deployments (default)
  - `create_event_broker()` factory function
  - Prepares for `RedisEventBroker` for distributed deployments
  - Swappable backends aligned with "Swappable Backends" philosophy

- **Lifecycle Module**: Bootstrap and runtime orchestration (`lifecycle.py`)
  - `Runtime` class for application lifecycle management
  - Handles config loading, DI container initialization, event bus setup
  - OS signal handling (SIGINT/SIGTERM) for graceful shutdown
  - `run_with_lifecycle()` helper for clean application startup
  - Decouples lifecycle concerns from Engine (Engine now purely processes I/O)

### Added - Capabilities & Tools
- **Approval Protocol**: Universal Human-in-the-Loop (`protocols/approval/`)
  - `ApprovalProtocol` for interface-agnostic approval flows
  - `ApprovalRequest` and `ApprovalDecision` data models
  - Event-driven approval (agent → event → interface → decision)
  - Works with any interface (Telegram buttons, Web UI, CLI prompts)
  - Replaces interface-specific approval logic

- **SessionManager**: Stateful code execution (`tools/dev_tools/session_manager.py`)
  - Persistent execution environments per chat_id
  - Variables persist between executions (like Jupyter/ChatGPT Code Interpreter)
  - Session isolation (different users don't share state)
  - Automatic cleanup of idle sessions
  - Support for Docker containers and Jupyter kernels
  - Prepares PocketPortal for true "One-for-All" stateful interactions

- **MCP Security Policy**: Granular access control (`protocols/mcp/security_policy.py`)
  - `MCPSecurityPolicy` for controlling MCP server permissions
  - `FileSystemPolicy`: Restrict filesystem access to specific paths
  - `NetworkPolicy`: Control network access by domain and port
  - `ResourcePolicy`: Limit CPU, memory, disk usage
  - Predefined policies: `SANDBOXED_POLICY`, `TRUSTED_POLICY`, `UNRESTRICTED_POLICY`
  - Prevents MCP servers from having unrestricted system access

### Added - Operational Excellence
- **Cost Tracking Middleware**: Business metrics for LLM usage (`middleware/cost_tracker.py`)
  - `CostTracker` calculates estimated costs per interaction
  - Tracks costs per user, per model
  - Model pricing database (OpenAI, Anthropic Claude, local models)
  - Prevents "bill shock" in enterprise deployments
  - Exportable cost summaries

- **Secret Management Provider**: Abstract secret loading (`config/secrets.py`)
  - `SecretProvider` ABC for multiple backends
  - `EnvSecretProvider` for environment variables (default)
  - `DockerSecretProvider` for Docker Swarm/Compose secrets
  - `CompositeSecretProvider` to try multiple providers
  - Production-ready secret management (no hardcoded `os.getenv`)

### Changed - Structure Consolidation
- **Security Consolidation**: Moved `core/security_middleware.py` → `security/middleware.py`
  - Consolidates all security logic in `security/` package
  - Reduces surface area of `core/` package
  - Core now strictly handles orchestration (Engine, Context, Events)

- **Media Tools Organization**: Moved `audio_tools/` → `media_tools/audio/`
  - Future-proofs for video and image processing tools
  - `media_tools/audio/`, `media_tools/video/` (future), `media_tools/image/` (future)
  - Cleaner taxonomy for media processing

### Changed - Documentation Updates
- **README.md**: Updated project structure diagram
  - Removed references to deprecated `mcp_tools/` (now in `protocols/mcp/`)
  - Added new packages: `protocols/approval/`, `lifecycle.py`, `middleware/`
  - Reflects actual v4.5.0 structure

### Technical Improvements
- All new modules follow established patterns:
  - DAO pattern for swappable backends (EventBroker, SecretProvider)
  - Abstract interfaces for extensibility
  - Factory functions for instantiation
  - Comprehensive docstrings and examples
- Added `distributed` optional dependency group (Redis support for future EventBroker)
- Updated all imports to reflect new package structure

## [4.4.1] - 2025-12-18

### Added
- **Version SSOT (Single Source of Truth)**: All version references now dynamically fetch from `pyproject.toml` using `importlib.metadata`
  - Eliminates version drift across `__init__.py`, `cli.py`, and documentation
  - Fallback to '0.0.0-dev' for development environments

- **ToolManifest Schema**: Comprehensive tool metadata system (`tools/manifest.py`)
  - `TrustLevel` enum: CORE (0), VERIFIED (1), UNTRUSTED (2)
  - `SecurityScope` enum: READ_ONLY, READ_WRITE, SYSTEM_MODIFY, NETWORK_ACCESS, PRIVILEGED
  - `ResourceProfile` enum: LIGHTWEIGHT, NORMAL, CPU_INTENSIVE, IO_INTENSIVE, NETWORK_INTENSIVE
  - Automatic security policy enforcement (UNTRUSTED tools must use sandbox)
  - Helper functions: `create_core_manifest()`, `create_plugin_manifest()`, `create_untrusted_manifest()`

- **Dead Letter Queue (DLQ) CLI Commands**: Full job queue management via CLI
  - `pocketportal queue list [--status STATUS] [--limit N]`: List jobs by status
  - `pocketportal queue failed [--limit N]`: View failed jobs (DLQ)
  - `pocketportal queue retry <job_id>`: Retry a failed job
  - `pocketportal queue stats`: Show queue statistics
  - `pocketportal queue cleanup [--older-than-hours N]`: Clean up old jobs

- **Configuration Schemas**: Pydantic schemas for type-safe configuration (`config/schemas/`)
  - `SettingsSchema`: Root configuration with validation
  - `InterfaceConfig`, `SecurityConfig`, `LLMConfig`, `ObservabilityConfig`, `JobQueueConfig`
  - Strict validation with `extra = "forbid"` to reject unknown fields
  - Self-documenting configuration structure

### Changed
- **MCP Migration Completed**: Removed deprecated `tools/mcp_tools/` directory
  - All MCP code now in `protocols/mcp/` (migration from v4.4.0)
  - No more split logic or ambiguous imports

- **Test Organization**: Reorganized test suite into `tests/unit/` and `tests/integration/`
  - All current tests moved to `tests/unit/`
  - Created `tests/integration/README.md` with guidelines for integration tests
  - Enforces distinction between fast unit tests and slow integration tests

- **Documentation Cleanup**: Archived old strategic plans
  - `docs/STRATEGIC_PLAN_V4.3.md` → `docs/archive/STRATEGIC_PLAN_V4.3_EXECUTED.md`
  - Reduces cognitive load by removing completed planning documents from active docs

### Fixed
- **Version Drift**: Fixed inconsistent version numbers across codebase
  - `pocketportal/__init__.py` was 4.3.0 (now dynamically fetched)
  - `pocketportal/cli.py` was 4.1.1 (now dynamically fetched)
  - All now reference `pyproject.toml` as single source

### Technical Debt Reduction
- Removed redundant MCP implementation from `tools/`
- Standardized test structure for better maintainability
- Created foundation for stricter configuration validation
- Established tool manifest pattern for future security enhancements

## [4.4.0] - 2025-12-17

### Added - Phase 2: Async Job Queue
- **Job Repository Interface**: Abstract interface following DAO pattern for swappable backends
  - `JobRepository` with `Job`, `JobStatus`, and `JobPriority` classes in `persistence/repositories.py`
  - Support for pending, running, completed, failed, cancelled, and retrying statuses
  - Priority queue support (LOW, NORMAL, HIGH, CRITICAL)
  - Job retry mechanism with configurable max retries
  - Worker assignment tracking
  - Stale job detection and requeuing

- **In-Memory Job Queue**: Fast, thread-safe implementation
  - `InMemoryJobRepository` in `persistence/inmemory_impl.py`
  - asyncio.Queue-based priority queue with heap implementation
  - Thread-safe operations with async locks
  - Automatic cleanup of old completed jobs
  - Batch job operations

- **Background Worker System**: Async job processing
  - `JobWorker` class for individual workers in `core/job_worker.py`
  - `JobWorkerPool` for managing multiple concurrent workers
  - `JobHandler` interface for pluggable job execution logic
  - `JobRegistry` for mapping job types to handlers
  - Event bus integration for real-time status updates
  - Automatic retry on failure
  - Graceful shutdown with timeout
  - Periodic cleanup of stale jobs

### Added - Phase 3: MCP Protocol Elevation
- **Protocols Package**: First-class protocol integrations
  - Created `pocketportal/protocols/` directory for protocol-level integrations
  - Moved MCP from `tools/mcp_tools/` to `protocols/mcp/`
  - Protocol-level features distinguished from user-facing tools

- **Bidirectional MCP Support**: Full mesh networking
  - `MCPServer` class in `protocols/mcp/mcp_server.py`
  - Expose PocketPortal tools as MCP server
  - Allow other applications to connect and use PocketPortal tools
  - Bidirectional communication (PocketPortal ↔ Other apps)
  - CLI command: `pocketportal mcp-server`

- **Universal Resource Resolver**: Unified resource access
  - `UniversalResourceResolver` in `protocols/resource_resolver.py`
  - Support for multiple URI schemes: file://, http://, https://, mcp://, db://
  - Pluggable `ResourceProvider` interface
  - Built-in providers:
    - `FileSystemProvider`: Local filesystem access
    - `WebProvider`: HTTP/HTTPS resources
    - `MCPProvider`: MCP resource access
    - `DatabaseProvider`: Database record access
  - Batch resource resolution
  - Unified `Resource` data model
  - Content type detection

### Added - Phase 4: Observability
- **Observability Package**: Production-grade monitoring
  - Created `pocketportal/observability/` directory
  - Comprehensive observability features for production deployments

- **OpenTelemetry Integration**: Distributed tracing
  - `setup_telemetry()` in `observability/tracer.py`
  - Automatic instrumentation for FastAPI and aiohttp
  - OTLP exporter support (Jaeger, Grafana Tempo compatible)
  - Manual span creation via `trace_operation()` context manager
  - Trace context propagation across services
  - Console exporter for debugging

- **Health Check System**: Kubernetes-ready probes
  - `HealthCheckSystem` in `observability/health.py`
  - Liveness probe: `/health/live` (is service running?)
  - Readiness probe: `/health/ready` (is service ready for traffic?)
  - Full health check: `/health` (detailed status of all components)
  - Pluggable health check providers
  - Built-in providers:
    - `DatabaseHealthCheck`: Database connection health
    - `JobQueueHealthCheck`: Job queue status
    - `WorkerPoolHealthCheck`: Worker pool status
  - Three-state health: healthy, degraded, unhealthy
  - Aggregated health across multiple components

- **Config Hot-Reloading**: Zero-downtime updates
  - `ConfigWatcher` in `observability/config_watcher.py`
  - Watch configuration files for changes
  - Automatic reload without restart
  - Support for YAML, JSON, and TOML formats
  - Config validation before applying changes
  - Automatic rollback on invalid config
  - Callback system for config change notifications
  - File hash-based change detection

- **Prometheus Metrics**: Production monitoring
  - `MetricsCollector` in `observability/metrics.py`
  - Prometheus-compatible metrics endpoint: `/metrics`
  - Standard metrics:
    - HTTP request counters and duration histograms
    - Job queue metrics (enqueued, completed, pending, running)
    - Worker pool metrics (total, busy, idle)
    - LLM request metrics (requests, duration, tokens)
    - Error counters by type and component
  - `MetricsMiddleware` for automatic HTTP metrics collection
  - Custom metric registration support

### Changed
- **Security Middleware**: Fixed import path
  - Updated `core/security_middleware.py` to use correct import path
  - Changed from `from security.security_module` to `from pocketportal.security.security_module`

### Technical Improvements
- All phases include comprehensive test suites:
  - `test_phase2_standalone.py`: 7 tests for job queue system
  - `test_phase3_standalone.py`: 7 tests for MCP protocol and resource resolution
  - `test_phase4_standalone.py`: 6 tests for observability features
- All tests implement closed-loop testing (Carmack methodology)
- Independent verification without user involvement
- Total test coverage: 20 automated tests

## [4.3.0] - 2025-12-XX

### Added
- Plugin ecosystem via entry points
- OpenTelemetry observability foundation
- Testing infrastructure with pytest markers
- Strategic planning documentation
- Documentation consolidation

### Changed
- Merged root docs into `docs/` directory
- Consistent versioning across all files

## [4.2.0] - 2025-XX-XX

### Added
- DAO pattern for persistence layer
- Dynamic tool discovery
- Lazy loading for heavy dependencies
- Abstract repositories (ConversationRepository, KnowledgeRepository)

### Performance
- Startup time improved from ~3s to <500ms

## [4.1.0] - 2025-XX-XX

### Added
- Unified CLI with `pocketportal` command
- Pydantic settings for type-safe configuration
- BaseInterface ABC for consistent interface contract
- Deployment configurations (systemd, launchd)

## [4.0.0] - 2025-XX-XX

### Added
- Complete architectural refactor
- Interface-agnostic design
- Dependency injection
- Event bus for real-time feedback
- Structured logging with JSON
- Externalized prompts
- SQLite rate limiting
- Custom exception types

### Migration
- See `docs/archive/MIGRATION_TO_4.0.md` for upgrade path from 3.x

## [3.x] - Legacy

Previous monolithic architecture. See `docs/archive/` for historical documentation.

---

## Version Numbering

- **Major.Minor.Patch** (Semantic Versioning)
- Major: Breaking API changes
- Minor: New features, backward compatible
- Patch: Bug fixes, backward compatible

## Links

- [Repository](https://github.com/ckindle-42/pocketportal)
- [Issues](https://github.com/ckindle-42/pocketportal/issues)
