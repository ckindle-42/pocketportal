# PocketPortal - Testing Guide

**Comprehensive Testing Strategy & Best Practices**

---

## Table of Contents

1. [Overview](#overview)
2. [Test Organization](#test-organization)
3. [Test Types](#test-types)
4. [Running Tests](#running-tests)
5. [Test Markers](#test-markers)
6. [Writing Tests](#writing-tests)
7. [Code Coverage](#code-coverage)
8. [Continuous Integration](#continuous-integration)

---

## Overview

PocketPortal follows a comprehensive testing strategy with three levels of tests:

- **Unit Tests**: Fast, isolated tests with no external dependencies
- **Integration Tests**: Tests requiring Docker, network, or external services
- **End-to-End (E2E) Tests**: Full system tests validating complete workflows

**Testing Philosophy:**
- Write tests BEFORE fixing bugs (TDD for bug fixes)
- Maintain >80% code coverage for core modules
- Fast feedback loop (unit tests < 100ms each)
- Integration tests must be idempotent
- E2E tests validate production scenarios

---

## Test Organization

```
tests/
├── unit/                          # Fast unit tests (no I/O)
│   ├── test_base_tool.py         # Tool framework tests
│   ├── test_security.py          # Security module tests
│   ├── test_router.py            # Routing logic tests
│   ├── test_data_integrity.py    # Data validation tests
│   ├── test_human_in_loop_middleware.py  # Approval protocol tests
│   └── test_job_queue.py         # Job queue logic tests
│
├── integration/                   # Integration tests (external deps)
│   ├── README.md                 # Integration test guide
│   └── (database, Docker, network tests)
│
└── e2e/                          # End-to-end tests (full system)
    ├── README.md                 # E2E test guide
    ├── test_phase2_standalone.py # Job queue system tests
    ├── test_phase3_standalone.py # MCP protocol tests
    └── test_phase4_standalone.py # Observability tests
```

---

## Test Types

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual functions/classes in isolation

**Characteristics:**
- **Fast**: <100ms per test
- **No I/O**: No file system, network, or database access
- **Mocked Dependencies**: All external dependencies mocked
- **Deterministic**: Same input always produces same output

**What to Test:**
- Business logic
- Algorithm correctness
- Error handling
- Edge cases
- Input validation

**Example:**
```python
import pytest
from pocketportal.routing import TaskClassifier

def test_task_classifier_simple_query():
    classifier = TaskClassifier()
    result = classifier.classify("What's 2+2?")

    assert result.complexity == "LOW"
    assert result.estimated_tokens < 100
    assert "calculation" in result.tags

@pytest.mark.unit
def test_security_sanitization():
    from pocketportal.security import SecurityModule

    sanitizer = SecurityModule()

    # Test path traversal prevention
    malicious = "../../etc/passwd"
    clean = sanitizer.sanitize_path(malicious)
    assert ".." not in clean

    # Test command injection prevention
    malicious_cmd = "ls; rm -rf /"
    with pytest.raises(SecurityError):
        sanitizer.validate_command(malicious_cmd)
```

**Marker**: `@pytest.mark.unit`

---

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test interactions between components and external systems

**Characteristics:**
- **Slower**: 1-10 seconds per test
- **External Dependencies**: May require Docker, database, network
- **Real Implementations**: Use actual repositories, not mocks
- **Cleanup**: Must clean up resources after test

**What to Test:**
- Repository implementations (SQLite, PostgreSQL)
- LLM backend connections
- Docker sandbox execution
- File system operations
- Network requests

**Requirements:**
- Docker daemon running (for Docker tests)
- Network access (for API tests)
- Test databases (isolated from production)
- Environment variables for credentials

**Example:**
```python
import pytest
import docker
from pocketportal.persistence import SQLiteConversationRepository

@pytest.mark.integration
@pytest.mark.requires_docker
def test_docker_sandbox_execution():
    client = docker.from_env()

    # Test code execution in Docker sandbox
    sandbox = DockerSandbox(client)
    result = sandbox.execute_python("print('Hello, World!')")

    assert result.stdout == "Hello, World!\n"
    assert result.exit_code == 0

    # Cleanup
    sandbox.cleanup()

@pytest.mark.integration
def test_sqlite_repository_persistence():
    repo = SQLiteConversationRepository(":memory:")

    # Add messages
    await repo.add_message("user_123", "user", "Hello")
    await repo.add_message("user_123", "assistant", "Hi there!")

    # Retrieve and verify
    messages = await repo.get_messages("user_123")
    assert len(messages) == 2
    assert messages[0].content == "Hello"
```

**Marker**: `@pytest.mark.integration`

**Additional Markers**:
- `@pytest.mark.requires_docker`: Requires Docker daemon
- `@pytest.mark.requires_llm`: Requires running LLM backend

---

### 3. End-to-End Tests (`tests/e2e/`)

**Purpose**: Validate complete user workflows across entire system

**Characteristics:**
- **Slowest**: 10+ seconds per test
- **Full System**: All components running
- **Real Services**: Actual LLM, database, interfaces
- **Production-Like**: Mimics actual usage

**What to Test:**
- Complete user journeys
- Message processing pipeline
- Tool execution workflows
- Error recovery scenarios
- Performance under load

**Example:**
```python
import pytest
from pocketportal.core import create_agent_core
from pocketportal.interfaces.telegram import TelegramInterface

@pytest.mark.integration
@pytest.mark.slow
async def test_complete_message_flow():
    # Setup
    config = load_test_config()
    agent = create_agent_core(config)
    interface = TelegramInterface(agent, config)

    # Simulate user message
    message = "Generate a QR code for https://example.com"
    response = await interface.process_message("user_123", message)

    # Verify
    assert response.success
    assert "QR code" in response.text
    assert response.attachments[0].type == "image"

    # Cleanup
    await interface.stop()
    await agent.shutdown()

@pytest.mark.integration
@pytest.mark.slow
async def test_job_queue_end_to_end():
    # Test async job queue system
    queue = create_job_queue()
    worker_pool = JobWorkerPool(queue, num_workers=5)

    # Submit job
    job_id = await queue.submit_job(
        "heavy_computation",
        priority=JobPriority.HIGH,
        parameters={"input": "test_data"}
    )

    # Start workers
    await worker_pool.start()

    # Wait for completion
    result = await queue.wait_for_job(job_id, timeout=30)

    assert result.status == JobStatus.COMPLETED
    assert result.output is not None

    # Cleanup
    await worker_pool.stop()
```

**Marker**: `@pytest.mark.integration` (E2E tests are a subset of integration tests)

**Additional Markers**:
- `@pytest.mark.slow`: Tests taking >5 seconds

---

## Running Tests

### Basic Usage

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_security.py

# Run specific test function
pytest tests/unit/test_security.py::test_path_traversal_prevention
```

### By Test Type

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Exclude slow tests
pytest -m "not slow"

# Exclude tests requiring LLM
pytest -m "not requires_llm"
```

### With Coverage

```bash
# Generate coverage report
pytest --cov=pocketportal --cov-report=html

# View report
open htmlcov/index.html

# Show missing lines
pytest --cov=pocketportal --cov-report=term-missing

# Fail if coverage < 80%
pytest --cov=pocketportal --cov-fail-under=80
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Run unit tests in parallel
pytest -m unit -n auto
```

### Debugging

```bash
# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# More verbose output
pytest -vv

# Show print statements
pytest -s
```

---

## Test Markers

PocketPortal uses pytest markers to categorize and filter tests. Markers are defined in `pyproject.toml`.

### Available Markers

| Marker | Description | Usage |
|--------|-------------|-------|
| `unit` | Fast unit tests with no external dependencies | `pytest -m unit` |
| `integration` | Tests requiring Docker, network, or database | `pytest -m integration` |
| `slow` | Tests taking more than 5 seconds | `pytest -m slow` |
| `requires_llm` | Tests needing a running LLM backend | `pytest -m requires_llm` |
| `requires_docker` | Tests requiring Docker daemon | `pytest -m requires_docker` |

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    assert 1 + 1 == 2

@pytest.mark.integration
@pytest.mark.requires_docker
def test_docker_integration():
    # Docker-dependent test
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_long_running_integration():
    # Slow integration test
    pass

@pytest.mark.requires_llm
async def test_llm_backend():
    # LLM-dependent test
    pass
```

### Combining Markers

```bash
# Run integration tests but exclude slow ones
pytest -m "integration and not slow"

# Run all tests except those requiring Docker
pytest -m "not requires_docker"

# Run only fast unit tests
pytest -m "unit and not slow"
```

---

## Writing Tests

### Test Structure

Follow the **Arrange-Act-Assert** pattern:

```python
def test_example():
    # Arrange: Set up test data
    input_data = "test input"
    expected_output = "expected result"

    # Act: Execute the code under test
    actual_output = function_under_test(input_data)

    # Assert: Verify the results
    assert actual_output == expected_output
```

### Naming Conventions

- Test files: `test_<module>.py`
- Test functions: `test_<behavior>` or `test_<scenario>`
- Test classes: `Test<Component>`

**Good test names:**
```python
def test_qr_code_generates_valid_image()
def test_security_blocks_path_traversal()
def test_rate_limiter_rejects_after_limit()
def test_circuit_breaker_opens_after_failures()
```

**Bad test names:**
```python
def test_function1()  # Too vague
def test_case_1()     # Not descriptive
def test_error()      # What error?
```

### Fixtures

Use fixtures for common setup:

```python
import pytest
from pocketportal.core import AgentCore

@pytest.fixture
def agent_core():
    """Create AgentCore for testing"""
    config = create_test_config()
    core = AgentCore(config)
    yield core
    # Cleanup
    core.shutdown()

@pytest.fixture
def mock_llm_backend():
    """Mock LLM backend for testing"""
    backend = Mock(spec=LLMBackend)
    backend.generate.return_value = "Mocked response"
    return backend

def test_agent_processing(agent_core, mock_llm_backend):
    agent_core.llm_backend = mock_llm_backend
    result = agent_core.process_message("Hello")
    assert result == "Mocked response"
```

### Async Tests

Use `pytest-asyncio` for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_integration():
    repo = SQLiteConversationRepository(":memory:")
    await repo.add_message("user", "role", "content")
    messages = await repo.get_messages("user")
    assert len(messages) == 1
```

### Parameterized Tests

Test multiple scenarios efficiently:

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("WORLD", "WORLD"),
    ("Test123", "TEST123"),
])
def test_uppercase_conversion(input, expected):
    assert input.upper() == expected

@pytest.mark.parametrize("malicious_path", [
    "../../etc/passwd",
    "../../../root/.ssh/id_rsa",
    "..\\..\\windows\\system32",
])
def test_path_traversal_blocked(malicious_path):
    with pytest.raises(SecurityError):
        validate_path(malicious_path)
```

### Mocking

Use unittest.mock for isolating dependencies:

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    # Create mock
    mock_db = Mock()
    mock_db.get_user.return_value = {"id": 1, "name": "Test"}

    # Use mock
    result = function_using_db(mock_db)

    # Verify mock was called correctly
    mock_db.get_user.assert_called_once_with(user_id=1)

@patch('pocketportal.routing.ollama_client')
def test_llm_backend_call(mock_ollama):
    mock_ollama.generate.return_value = "Mocked LLM response"

    router = IntelligentRouter()
    response = router.route("Test query")

    assert response == "Mocked LLM response"
    mock_ollama.generate.assert_called_once()
```

---

## Code Coverage

### Generating Reports

```bash
# HTML report (recommended)
pytest --cov=pocketportal --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=pocketportal --cov-report=term

# Show missing lines
pytest --cov=pocketportal --cov-report=term-missing

# XML report (for CI)
pytest --cov=pocketportal --cov-report=xml
```

### Coverage Goals

- **Core modules** (`core/`, `routing/`, `security/`): >90%
- **Tools** (`tools/`): >80%
- **Interfaces** (`interfaces/`): >75%
- **Overall project**: >80%

### Excluding Files from Coverage

Add to `.coveragerc` or `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      docker:
        image: docker:dind

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run unit tests
        run: pytest -m unit --cov=pocketportal

      - name: Run integration tests
        run: pytest -m "integration and not requires_llm"

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Pre-Commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest-unit
        entry: pytest -m unit
        language: system
        pass_filenames: false
        always_run: true
```

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

---

## Best Practices

### 1. Test Independence
- Tests should NOT depend on each other
- Tests should be runnable in any order
- Use fixtures for setup, not other tests

### 2. Test One Thing
- Each test should verify one specific behavior
- If testing multiple scenarios, use parameterization
- Split complex tests into multiple smaller tests

### 3. Clear Assertions
```python
# Good: Clear what is being tested
assert response.status_code == 200
assert "error" not in response.json()

# Bad: Unclear what failed
assert response  # What are we checking?
```

### 4. Avoid Test Logic
```python
# Bad: Logic in tests makes them harder to understand
def test_with_logic():
    results = []
    for i in range(10):
        if i % 2 == 0:
            results.append(function(i))
    assert len(results) > 0

# Good: Simple, clear test
@pytest.mark.parametrize("input", [0, 2, 4, 6, 8])
def test_even_numbers(input):
    result = function(input)
    assert result is not None
```

### 5. Use Descriptive Error Messages
```python
# Good: Helpful error message
assert len(results) == 3, f"Expected 3 results, got {len(results)}: {results}"

# Better: Even more context
assert len(results) == 3, (
    f"Expected 3 results for query '{query}', "
    f"but got {len(results)}: {results}"
)
```

### 6. Clean Up Resources
```python
@pytest.fixture
def temp_database():
    db = create_database()
    yield db
    # Always cleanup, even if test fails
    db.close()
    os.remove(db.path)
```

---

## Troubleshooting

### Issue: Tests fail with import errors

```bash
# Ensure package is installed
pip install -e .

# Check Python path
python -c "import pocketportal; print(pocketportal.__file__)"
```

### Issue: "Docker daemon not running"

```bash
# Start Docker
sudo systemctl start docker

# Verify Docker is accessible
docker ps

# Skip Docker tests
pytest -m "not requires_docker"
```

### Issue: Tests are slow

```bash
# Run only unit tests (fast)
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Use parallel execution
pytest -n auto
```

### Issue: Flaky tests (intermittent failures)

- Add retries for network-dependent tests
- Increase timeouts for slow operations
- Mock external services
- Check for race conditions

```python
# Add retry decorator for flaky tests
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_flaky_network_operation():
    response = requests.get("https://api.example.com")
    assert response.status_code == 200
```

---

## Documentation

- **Architecture**: [docs/architecture.md](architecture.md)
- **Installation**: [docs/setup.md](setup.md)
- **Changelog**: [CHANGELOG.md](../CHANGELOG.md)

---

## Contributing

When contributing code:

1. **Write tests first** (TDD) for new features
2. **Ensure all tests pass** before submitting PR
3. **Maintain coverage** - don't decrease overall coverage
4. **Add markers** - use appropriate pytest markers
5. **Document tests** - add docstrings for complex tests

**PR Checklist:**
- [ ] All unit tests pass (`pytest -m unit`)
- [ ] Integration tests pass (`pytest -m integration`)
- [ ] Coverage is maintained or improved
- [ ] New features have corresponding tests
- [ ] Tests are properly marked
- [ ] No flaky tests introduced

---

**Last Updated**: December 2025
**Maintained By**: PocketPortal Team

For questions or issues: https://github.com/ckindle-42/pocketportal/issues
