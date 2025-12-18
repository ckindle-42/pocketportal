# Changelog

All notable changes to PocketPortal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
