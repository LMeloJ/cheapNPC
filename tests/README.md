# cheapNPC Test Suite

This directory contains a comprehensive test suite for the cheapNPC project, organized into proper unit and integration tests.

## Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                # Pytest configuration and shared fixtures
├── fixtures/
│   └── test_data.py           # Test data factories and fixtures
├── unit/
│   ├── test_models.py         # Unit tests for core models
│   ├── test_services.py       # Unit tests for services
│   └── test_agents.py         # Unit tests for AI agents
└── integration/
    ├── test_workflows.py      # Integration tests for workflows
    └── test_comprehensive.py  # Comprehensive tests consolidating original functionality
```

## Running Tests

### Using pytest directly:
```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=cheapNPC --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py
```

### Using the test runner:
```bash
# Run all tests
python run_tests.py

# Run unit tests only
python run_tests.py --type unit

# Run integration tests only
python run_tests.py --type integration

# Run with coverage
python run_tests.py --coverage

# Run in verbose mode
python run_tests.py --verbose
```

## Test Categories

### Unit Tests
- **test_models.py**: Tests for core data models (NPC, ItemQuality, InventoryEntry, etc.)
- **test_services.py**: Tests for service layer components (NPCService, TradingService, etc.)
- **test_agents.py**: Tests for AI agent functionality (NPCAgent, PlannerAgent, etc.)

### Integration Tests
- **test_workflows.py**: Tests for complete workflows and service integration
- **test_comprehensive.py**: Comprehensive tests that consolidate functionality from the original test files

### Fixtures
- **test_data.py**: Test data factories and sample data for consistent testing

## Test Features

- **Temporary Database**: Each test runs with a clean temporary database
- **Mocking**: Extensive use of mocks to isolate components and test behavior
- **Async Support**: Full support for testing async functions and coroutines
- **Fixtures**: Reusable test data and setup utilities
- **Coverage**: Built-in support for code coverage reporting

## Migration from Original Tests

This test suite replaces the following original test files:
- `test_npc_agent.py` → Consolidated into `test_comprehensive.py`
- `test_refactored_agents.py` → Consolidated into `test_comprehensive.py`
- `test_refactored_structure.py` → Consolidated into `test_comprehensive.py`

All functionality from the original tests has been preserved and organized into a proper test structure.

## Adding New Tests

When adding new tests:

1. **Unit tests** go in `tests/unit/` and test individual components in isolation
2. **Integration tests** go in `tests/integration/` and test complete workflows
3. **Test data** should be added to `tests/fixtures/test_data.py`
4. **Shared fixtures** should be added to `tests/conftest.py`

Follow the existing patterns and use appropriate mocking to ensure tests are fast and reliable.
