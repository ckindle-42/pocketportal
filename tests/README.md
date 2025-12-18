# PocketPortal Test Suite

Comprehensive test coverage for the PocketPortal v4.x modular architecture.

---

## Test Organization

Tests are organized by scope and dependencies:

```
tests/
├── unit/              # Fast, isolated unit tests (no I/O, no network)
├── integration/       # Integration tests (require Docker, network, database)
└── e2e/              # End-to-end functional tests (full system validation)
```

### Test Categories

**Unit Tests** (`tests/unit/`)
- ✅ Fast execution (< 1 second per test)
- ✅ No external dependencies (no network, no database, no Docker)
- ✅ Mocked external services
- ✅ Focus on business logic and algorithms

**Integration Tests** (`tests/integration/`)
- ⚠️ Require external services (Docker, Redis, etc.)
- ⚠️ Slower execution (1-10 seconds per test)
- ⚠️ Test component interactions
- ⚠️ Validate data flow between modules

**End-to-End Tests** (`tests/e2e/`)
- 🔴 Full system tests (complete workflows)
- 🔴 May require running LLM backends
- 🔴 Slowest execution (10+ seconds per test)
- 🔴 Validate production-like scenarios

---

## Current Test Files

### Unit Tests (`tests/unit/`)

| Test File | Description | Coverage |
|-----------|-------------|----------|
| `test_router.py` | Intelligent routing and task classification | ✅ Routing logic, strategy selection |
| `test_security.py` | Security sanitization and input validation | ✅ Path traversal, command injection, XSS prevention |
| `test_base_tool.py` | Base tool framework and parameter validation | ✅ Tool interface, parameter parsing, validation |
| `test_data_integrity.py` | Atomic writes, crash recovery, persistence | ✅ File locking, backup creation, corruption prevention |
| `test_human_in_loop_middleware.py` | Human approval protocol and middleware | ✅ Approval workflow, timeout handling, high-risk detection |
| `test_job_queue.py` | Async job queue system | ✅ Job scheduling, priority queues, retry logic |

### End-to-End Tests (`tests/e2e/`)

| Test File | Description | Requirements |
|-----------|-------------|--------------|
| `test_mcp_protocol.py` | Model Context Protocol integration | 🔴 Requires MCP server |
| `test_job_queue_system.py` | Job queue system (full workflow) | 🔴 Requires async runtime, database |
| `test_observability.py` | Observability stack (OpenTelemetry, Prometheus) | 🔴 Requires observability services |

---

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -e ".[dev]"
```

This installs:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `black` - Code formatting (for test development)
- `ruff` - Linting (for test development)
- `mypy` - Type checking (for test development)

### Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=pocketportal --cov-report=html --cov-report=term

# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test Categories

```bash
# Run only unit tests (fast, no external dependencies)
pytest tests/unit/ -v

# Run only integration tests (requires external services)
pytest tests/integration/ -v -m integration

# Run only end-to-end tests (full system)
pytest tests/e2e/ -v

# Run specific test file
pytest tests/unit/test_router.py -v

# Run specific test function
pytest tests/unit/test_router.py::test_classify_task_code -v
```

### Run Tests by Marker

Tests are marked with pytest markers for selective execution:

```bash
# Run only fast unit tests
pytest -m unit -v

# Run only integration tests (requires Docker/network)
pytest -m integration -v

# Skip slow tests
pytest -m "not slow" -v

# Run tests requiring LLM backend
pytest -m requires_llm -v

# Run tests requiring Docker
pytest -m requires_docker -v
```

**Available Markers:**
- `unit` - Fast unit tests with no external dependencies
- `integration` - Integration tests requiring Docker, network, or database
- `slow` - Tests taking more than 5 seconds
- `requires_llm` - Tests requiring a running LLM backend (Ollama, etc.)
- `requires_docker` - Tests requiring Docker to be running

### Parallel Test Execution

Run tests in parallel for faster execution:

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests on 4 cores
pytest tests/ -n 4

# Run unit tests in parallel (safe, no I/O conflicts)
pytest tests/unit/ -n auto
```

---

## Test Coverage Goals

| Module | Current Coverage | Target Coverage |
|--------|-----------------|-----------------|
| `pocketportal.routing` | ✅ High | 90%+ |
| `pocketportal.security` | ✅ High | 95%+ (critical) |
| `pocketportal.core.interfaces` | ✅ Good | 85%+ |
| `pocketportal.core.registries` | ⚠️ Medium | 80%+ |
| `pocketportal.tools` | ⚠️ Medium | 70%+ |
| `pocketportal.protocols.mcp` | 🔴 Low | 75%+ |
| `pocketportal.observability` | 🔴 Low | 70%+ |

**Priority for New Tests:**
1. Security-critical code (input sanitization, rate limiting)
2. Core business logic (routing, job queue, context management)
3. Tool implementations (especially high-risk tools)
4. Interface implementations (Telegram, Web, etc.)

---

## Adding New Tests

### Test File Naming Convention

Follow the functional naming convention (not "phase" naming):

✅ **Good:**
- `test_router.py` - Clear, describes what's being tested
- `test_job_queue_system.py` - Descriptive, functional name
- `test_data_integrity.py` - Clear purpose

❌ **Bad:**
- `test_phase_1.py` - Vague, version-specific
- `test_old_router.py` - Unclear, contains "old"
- `test_v4_features.py` - Version-specific, not descriptive

### Test Structure Template

```python
"""
Test module for [feature/component name]

Tests cover:
- [Functionality area 1]
- [Functionality area 2]
- [Edge cases and error handling]
"""

import pytest
from pocketportal.[module] import [ClassToTest]


class Test[FeatureName]:
    """Test suite for [feature description]"""

    @pytest.fixture
    def setup_fixture(self):
        """Setup test fixtures"""
        # Setup code
        yield fixture_data
        # Teardown code

    def test_[feature]_positive_case(self, setup_fixture):
        """Test [feature] with valid input"""
        # Arrange
        input_data = ...

        # Act
        result = ...

        # Assert
        assert result == expected

    def test_[feature]_edge_case(self, setup_fixture):
        """Test [feature] with edge case input"""
        # Test edge cases

    def test_[feature]_error_handling(self, setup_fixture):
        """Test [feature] error handling"""
        with pytest.raises(ExpectedError):
            # Test error conditions


    @pytest.mark.asyncio
    async def test_[async_feature](self):
        """Test async [feature]"""
        result = await async_function()
        assert result is not None
```

### Adding Test Markers

Mark tests appropriately for selective execution:

```python
import pytest


@pytest.mark.unit
def test_fast_logic():
    """Fast unit test"""
    pass


@pytest.mark.integration
@pytest.mark.requires_docker
def test_docker_integration():
    """Integration test requiring Docker"""
    pass


@pytest.mark.slow
@pytest.mark.requires_llm
async def test_llm_workflow():
    """Slow E2E test requiring LLM backend"""
    pass
```

### Test Documentation

Each test should include:
1. **Docstring**: Describe what the test validates
2. **Clear test name**: `test_feature_scenario` (e.g., `test_router_handles_invalid_input`)
3. **Arrange-Act-Assert**: Clear separation of setup, execution, and validation
4. **Error messages**: Descriptive assertion messages

```python
def test_router_classifies_code_tasks_correctly():
    """Test that IntelligentRouter correctly identifies code-related tasks"""
    # Arrange
    router = IntelligentRouter()
    code_query = "Write a Python function to reverse a string"

    # Act
    classification = router.classify_task(code_query)

    # Assert
    assert classification.task_type == "code", \
        f"Expected 'code' classification, got '{classification.task_type}'"
    assert classification.complexity == "moderate"
```

---

## Continuous Integration

Tests are automatically run on:
- ✅ Pull request creation
- ✅ Commits to main branch
- ✅ Release tags

**CI Configuration:** See `.github/workflows/` (if configured)

**Pre-commit Hooks:**
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Hooks run automatically on git commit:
# - black (code formatting)
# - ruff (linting)
# - pytest (fast unit tests only)
```

---

## Debugging Tests

### Run Tests with Verbose Output

```bash
# Show print statements
pytest tests/ -v -s

# Show local variables on failure
pytest tests/ -v -l

# Drop into debugger on failure
pytest tests/ -v --pdb
```

### Use pytest Fixtures for Debugging

```python
@pytest.fixture
def debug_fixture():
    """Fixture with debug logging"""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    yield
    logging.basicConfig(level=logging.INFO)
```

---

## Related Documentation

- **Architecture Guide**: [docs/architecture.md](../docs/architecture.md)
- **Testing Guide**: [docs/TESTING.md](../docs/TESTING.md)
- **Changelog**: [CHANGELOG.md](../CHANGELOG.md)
- **Contributing**: See README.md

---

## Test Quality Guidelines

### ✅ Good Test Practices

1. **Test one thing per test**: Each test should validate a single behavior
2. **Use descriptive names**: `test_router_handles_empty_query` > `test_router_1`
3. **Independent tests**: Tests should not depend on execution order
4. **Fast unit tests**: Unit tests should run in < 1 second
5. **Mock external services**: Unit tests should not make network calls
6. **Clear assertions**: Use descriptive error messages
7. **Test edge cases**: Empty inputs, null values, boundary conditions
8. **Test error paths**: Validate error handling and exceptions

### ❌ Bad Test Practices

1. **Vague test names**: `test_feature_1`, `test_phase_2`
2. **Multiple assertions**: Testing unrelated behaviors in one test
3. **Test interdependencies**: Test B depends on Test A running first
4. **Slow unit tests**: Unit test takes 10+ seconds (should be integration test)
5. **Hardcoded values**: Magic numbers without explanation
6. **Flaky tests**: Tests that randomly fail due to timing issues
7. **No cleanup**: Tests leave behind temp files or database records
8. **Skipped tests**: Tests marked with `@pytest.skip` without explanation

---

**Maintained By:** PocketPortal Development Team
**Last Updated:** 2025-12-18
**Version:** 4.7.4
