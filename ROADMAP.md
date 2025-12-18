# PocketPortal Roadmap

**Last Updated:** 2025-12-18
**Current Version:** v4.7.3
**Status:** Active Development

---

## Overview

This roadmap outlines planned enhancements and future development for PocketPortal. All items are forward-looking and represent work that has not yet been implemented.

**Current Project Health:** ✅ EXCELLENT
- Production-ready reliability features complete
- Clean architecture with minimal technical debt
- Comprehensive documentation and testing

---

## Recommended Next Steps (v4.8.0)

### Priority 1: Production Readiness

#### 1. Redis Queue Backend
**Status:** Planned
**Priority:** MEDIUM
**Effort:** 2-3 days
**Impact:** HIGH (enables multi-instance deployments)

**Description:**
Currently, the job queue uses an in-memory implementation suitable for single-instance deployments. Adding a Redis backend will enable distributed deployments with multiple PocketPortal instances sharing a common job queue.

**Implementation:**
- Create `src/pocketportal/persistence/redis_impl.py`
- Implement `RedisJobRepository` following the existing repository pattern
- Add Redis to `[distributed]` optional dependencies
- Create integration tests in `tests/integration/test_redis_queue.py`

**Benefits:**
- Horizontal scaling across multiple instances
- Job queue persistence across restarts
- Production-grade distributed architecture

---

#### 2. Pre-commit Hooks
**Status:** Planned
**Priority:** MEDIUM
**Effort:** 0.5 days
**Impact:** MEDIUM (enforces code quality automatically)

**Description:**
Add pre-commit hook configuration to automatically enforce code quality standards before commits.

**Implementation:**
- Create `.pre-commit-config.yaml` with black, ruff, and pytest hooks
- Add pre-commit to `[dev]` dependencies
- Document pre-commit setup in development guide

**Benefits:**
- Consistent code formatting across contributors
- Catch linting issues before commit
- Reduced code review overhead

---

### Priority 2: Developer Experience

#### 3. Reference Plugin Package
**Status:** Documented
**Priority:** MEDIUM
**Effort:** 1 day
**Impact:** MEDIUM (accelerates ecosystem growth)

**Description:**
Create an example plugin package to demonstrate third-party tool development. The plugin system is fully functional, but a reference implementation would help onboard external developers.

**Implementation:**
- Create separate repository: `pocketportal-tool-example`
- Implement simple tool (e.g., stock ticker, weather API, or currency converter)
- Include complete pyproject.toml with entry points
- Add comprehensive README with step-by-step guide
- Publish to PyPI as installable example

**Benefits:**
- Easier plugin ecosystem growth
- Clear example for third-party developers
- Validates plugin architecture in real-world scenario

---

#### 4. Semantic Release Automation
**Status:** Planned
**Priority:** LOW
**Effort:** 1 day
**Impact:** LOW (operational improvement)

**Description:**
Automate version management using conventional commits and python-semantic-release to reduce manual version updates and prevent drift.

**Implementation:**
- Add python-semantic-release to `[dev]` dependencies
- Configure `[tool.semantic_release]` in pyproject.toml
- Create conventional commits guide for contributors
- Integrate with CI/CD pipeline for automated releases

**Benefits:**
- Eliminates manual version bumps
- Automatic changelog generation
- Consistent versioning across files

---

#### 5. Tool Catalog Generator
**Status:** Planned
**Priority:** LOW
**Effort:** 0.5 days
**Impact:** LOW (documentation automation)

**Description:**
Automate tool documentation generation by scanning tool docstrings and manifests.

**Implementation:**
- Create `scripts/generate_tool_catalog.py`
- Extract tool name, description, parameters from manifests
- Generate `docs/TOOLS_CATALOG.md` with formatted output
- Add to pre-commit hooks to keep docs in sync

**Benefits:**
- Documentation stays synchronized with code
- Comprehensive tool reference for users
- Reduced manual documentation maintenance

---

## Future Enhancements (v4.9+)

### Advanced Capabilities (Research Phase)

#### Jupyter Kernel Integration
**Status:** Research
**Priority:** LOW
**Effort:** 5+ days
**Target:** v4.9+

**Description:**
Enhance the existing SessionManager to support full Jupyter kernel integration for notebook-like stateful execution.

**Exploration Needed:**
- Jupyter kernel protocol integration
- IPython execution environment compatibility
- Session isolation and resource cleanup
- Security implications of long-running kernels

**Decision Point:** Implement only if users request notebook-like experience

---

#### GraphRAG (Knowledge Graph)
**Status:** Research
**Priority:** LOW
**Effort:** 10+ days
**Target:** v5.0+

**Description:**
Extend the knowledge base system with graph-based relationship mapping and entity extraction.

**Exploration Needed:**
- Graph database selection (Neo4j vs. NetworkX)
- Knowledge extraction and entity recognition pipeline
- Query optimization and performance
- Integration with existing semantic search

**Decision Point:** Implement when clear use cases emerge from users

---

## Features NOT Recommended

### Breaking Changes (v5.0)
**Status:** Deferred
**Rationale:** Current architecture is solid and well-designed

Potential breaking changes are deferred until significant justification exists:
- Database migration (SQLite → PostgreSQL default)
- Configuration format changes (YAML → TOML)
- API redesigns

**Decision Point:** Only pursue if compelling user demand or architectural necessity

---

## Contribution Guidelines

### Proposing New Features

1. **Open GitHub Issue** with feature proposal
2. **Discuss scope and priority** with maintainers
3. **Review architectural fit** with existing patterns
4. **Create implementation plan** before coding
5. **Submit PR with tests and documentation**

### Priority Definitions

- **HIGH:** Critical for production scaling or reliability
- **MEDIUM:** Valuable for user experience or developer productivity
- **LOW:** Nice-to-have improvements or automation

---

## Version Planning

### v4.8.0 Focus
**Theme:** Production Scaling & Developer Experience
**Timeline:** 1-2 weeks (estimated 5-7 development days)

**Must-Have:**
- Redis queue backend
- Pre-commit hooks

**Should-Have:**
- Reference plugin package
- Semantic release automation

**Could-Have:**
- Tool catalog generator

---

## Maintenance Commitment

- ✅ **Bug fixes:** Addressed promptly in patch releases
- ✅ **Security updates:** Highest priority
- ✅ **Documentation:** Kept synchronized with code
- ✅ **Backward compatibility:** Maintained except in major versions

---

## Community Feedback

Feature requests and roadmap input welcome via:
- **GitHub Issues:** https://github.com/ckindle-42/pocketportal/issues
- **Discussions:** https://github.com/ckindle-42/pocketportal/discussions

---

**Next Review:** After v4.8.0 release
**Roadmap Maintained By:** PocketPortal Core Team
