# PocketPortal Test Suite

This directory contains tests for the PocketPortal project.

## Test Files

- `test_router.py` - Tests for intelligent routing and task classification
- `test_security.py` - Tests for security module (path traversal, command injection, XSS prevention)
- `test_base_tool.py` - Tests for base tool framework and parameter validation

## Running Tests

Install pytest if not already installed:
```bash
pip install pytest pytest-asyncio
```

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_router.py -v
```

Run with coverage:
```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

## Test Coverage

Current test coverage focuses on:
- ✅ Intelligent routing logic
- ✅ Security sanitization (path traversal, command injection, XSS)
- ✅ Base tool parameter validation
- ⚠️ Individual tool implementations (add as needed)

## Adding New Tests

When adding new tools or features, add corresponding tests:
1. Create test file: `tests/test_<module>.py`
2. Follow existing pattern with pytest
3. Include both positive and negative test cases
4. Test security implications
