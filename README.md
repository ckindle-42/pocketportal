# PocketPortal

PocketPortal is a modular platform for building conversational interfaces to local LLMs. It provides multiple interface options (Telegram, web), a plugin-based tool system, and architectural patterns for managing context, events, and asynchronous operations.

## Key Capabilities

- Multiple interface support (Telegram bot via CLI, FastAPI web interface via uvicorn, WebSocket)
- Modular tool framework with dynamic registration
- Shared conversation context across interfaces
- Event-driven architecture with real-time feedback
- Asynchronous job queue for background processing
- Model Context Protocol (MCP) support (client and server)
- OpenTelemetry integration for tracing and metrics
- SQLite-based rate limiting and persistence
- Structured logging with JSON output
- Component health monitoring and watchdog system

## Quick Start

```bash
# Install core dependencies
pip install -e .

# Verify installation
pocketportal --version
pocketportal validate-config

# Start Telegram interface
pocketportal start --interface telegram

# Start web interface (use uvicorn directly)
uvicorn pocketportal.interfaces.web.server:app --port 8000

# List available tools
pocketportal list-tools
```

## Optional Dependency Profiles

Install additional features as needed:

```bash
# Tool support (QR codes, web scraping)
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

# Docker sandboxing for code execution
pip install -e ".[security]"

# Development tools (pytest, black, mypy)
pip install -e ".[dev]"

# Install all features
pip install -e ".[all]"
```

**Common combinations:**
- Minimal: Core only (no extras)
- Personal use: `pip install -e ".[tools,documents,audio]"`
- Production: `pip install -e ".[observability,security,distributed]"`
- Development: `pip install -e ".[dev,all]"`

## Configuration

PocketPortal uses `.env` files and `config.yaml` for configuration. See [`docs/setup.md`](docs/setup.md) for detailed installation and configuration instructions.

## Documentation

- **[Architecture Guide](docs/architecture.md)** - System design and component overview
- **[Setup Guide](docs/setup.md)** - Installation and configuration
- **[Plugin Development](docs/PLUGIN_DEVELOPMENT.md)** - Creating custom tools and extensions
- **[Security Fixes](docs/security/SECURITY_FIXES.md)** - Security enhancements and fixes
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## Project Structure

```
pocketportal/
├── src/pocketportal/          # Main package (src-layout)
│   ├── core/                  # Agent engine, context, events, job queue
│   ├── interfaces/            # Telegram, web (FastAPI + WebSocket)
│   ├── protocols/             # MCP, approval workflows, resource resolution
│   ├── routing/               # Model routing logic
│   ├── security/              # Security middleware, sandboxing
│   ├── tools/                 # Tool framework and implementations
│   ├── observability/         # OpenTelemetry, metrics, health checks
│   ├── persistence/           # DAO pattern repositories
│   └── config/                # Configuration schemas
├── tests/                     # Test suite (unit, integration, e2e)
├── docs/                      # Documentation
├── pyproject.toml             # Package configuration (version SSOT)
└── CHANGELOG.md               # Release history
```

For a detailed breakdown of the architecture, see [`docs/architecture.md`](docs/architecture.md).

**Note:** This project uses src-layout. Install the package (even for development) to enable imports: `pip install -e .`

## Versioning & Releases

PocketPortal follows semantic versioning (Major.Minor.Patch).

**Single Source of Truth:**
- `pyproject.toml` is the authoritative source for the current version
- All version references are fetched from `pyproject.toml` via `importlib.metadata`

**Release requirements:**
1. Update version in `pyproject.toml`
2. Add dated entry to `CHANGELOG.md` (format: `## [X.Y.Z] - YYYY-MM-DD`)
3. Ensure all tests pass
4. Create git tag matching version (e.g., `v4.7.4`)

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

Contributions should follow the existing architectural patterns:

- **Tools**: Add new capabilities by implementing the `BaseTool` interface
- **Interfaces**: Add new user-facing channels by implementing `BaseInterface`
- **Protocols**: Add external protocol integrations (e.g., MCP providers)

Before making core architecture changes, open an issue for discussion. See [`docs/GOVERNANCE.md`](docs/GOVERNANCE.md) for contribution guidelines and [`docs/PLUGIN_DEVELOPMENT.md`](docs/PLUGIN_DEVELOPMENT.md) for creating plugins.

## License

MIT
