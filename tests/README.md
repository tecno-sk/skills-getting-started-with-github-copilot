# FastAPI Testing Suite

This directory contains comprehensive tests for the High School Management System FastAPI application.

## Test Structure

The testing suite is organized into several test files:

### 📋 `test_app.py` - Unit Tests
Core functionality tests for all API endpoints:

- **TestRootEndpoint**: Tests root URL redirection
- **TestGetActivities**: Tests retrieving activities list
- **TestSignupForActivity**: Tests student signup functionality
- **TestUnregisterFromActivity**: Tests student unregistration
- **TestEndToEndWorkflows**: Complete workflow tests
- **TestDataConsistency**: Data persistence and consistency tests

### 🔗 `test_integration.py` - Integration Tests
Real-world scenario tests:

- **TestIntegrationScenarios**: Full student workflows, capacity management
- **TestErrorHandlingAndEdgeCases**: Edge cases, malformed requests, concurrent operations

### ⚡ `test_performance.py` - Performance Tests
Performance and stress tests:

- **TestPerformance**: Response time and throughput tests
- **TestDataIntegrity**: Data consistency under load

### ⚙️ `conftest.py` - Test Configuration
Shared fixtures and test setup:

- `client`: FastAPI test client
- `reset_activities`: Resets activity data between tests
- `sample_activity`: Sample test data
- `test_email`: Test email fixture

## Running Tests

### Using the Test Runner Script

```bash
# Run all tests with coverage
python run_tests.py all

# Run only unit tests
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run only performance tests
python run_tests.py performance

# Run quick unit tests (fail fast)
python run_tests.py quick

# Generate HTML coverage report
python run_tests.py coverage
```

### Using pytest directly

```bash
# Run all tests with verbose output and coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_app.py -v

# Run specific test class
pytest tests/test_app.py::TestSignupForActivity -v

# Run specific test
pytest tests/test_app.py::TestSignupForActivity::test_signup_for_existing_activity_success -v

# Run tests with HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Run tests and stop on first failure
pytest tests/ -x
```

## Test Coverage

The test suite achieves **100% code coverage** of the FastAPI application:

- All API endpoints are tested
- All error conditions are covered
- All success paths are verified
- Edge cases and data integrity are validated

## Dependencies

The testing requires these additional packages (already in `requirements.txt`):

- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for FastAPI testing

## Test Features

### 🔄 Automatic Data Reset
Each test runs with a clean slate - the `reset_activities` fixture ensures that activity data is restored to its initial state before each test.

### 🎯 Comprehensive Coverage
- **API Endpoints**: All routes tested (GET, POST, DELETE)
- **Error Handling**: 404, 400, and validation errors
- **Data Integrity**: Participant lists, state consistency
- **Performance**: Response times and throughput
- **Integration**: End-to-end workflows

### 🧪 Test Categories

1. **Unit Tests**: Individual function/endpoint testing
2. **Integration Tests**: Multi-step workflows and scenarios
3. **Performance Tests**: Speed and efficiency validation
4. **Error Handling Tests**: Edge cases and error conditions

### 📊 Performance Benchmarks

The performance tests validate:
- Response time < 10ms per request (average)
- Batch operations complete within reasonable time
- Data consistency maintained under load

## Adding New Tests

When adding new functionality to the API:

1. Add unit tests to `test_app.py` for basic functionality
2. Add integration tests to `test_integration.py` for workflows
3. Add performance tests to `test_performance.py` if needed
4. Update fixtures in `conftest.py` if new test data is needed

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use descriptive names that explain what is being tested

### Example Test Structure

```python
class TestNewFeature:
    """Test description for the new feature."""
    
    def test_success_case(self, client, reset_activities):
        """Test successful operation."""
        # Arrange
        # Act
        # Assert
        
    def test_error_case(self, client, reset_activities):
        """Test error condition."""
        # Arrange
        # Act
        # Assert
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- Fast execution (< 2 seconds for full suite)
- No external dependencies
- Deterministic results
- Clear failure messages

## Configuration

Test configuration is in `pytest.ini`:

- Test discovery paths
- Pytest options
- Test markers for categorization
- Output formatting options