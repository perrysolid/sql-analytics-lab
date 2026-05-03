# Test Suite for SQL Playgrounds

This directory contains comprehensive tests for the SQL Playgrounds Docker environment.

## Test Structure

### Test Categories

1. **Docker Setup Tests** (`test_docker_setup.py`)
   - Container connectivity (PostgreSQL, PGAdmin, Superset)
   - Service health checks
   - Configuration validation

2. **Data Loading Tests** (`test_data_loading.py`)
   - Database schema validation
   - Data integrity checks
   - Geospatial data validation
   - Hash-based duplicate prevention

3. **Configuration Tests** (embedded in other test files)
   - File structure validation
   - Environment configuration
   - Volume mounting verification

### Prerequisites

1. **Docker Environment Running**:
   ```bash
   docker-compose up -d --build
   ```

2. **Install Test Dependencies**:
   ```bash
   pip install -r tests/requirements-test.txt
   ```

## Running Tests

### Run All Tests
```bash
# From project root
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Docker setup tests only
pytest tests/test_docker_setup.py -v

# Data loading tests only
pytest tests/test_data_loading.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Tests with Container Wait
```bash
# Tests will wait for containers to be ready
pytest tests/ -v -s
```

## Test Configuration

### Fixtures Available

- `postgres_connection`: Database connection for tests
- `wait_for_containers`: Waits for all services to be ready
- `sample_query_runner`: Helper for running database queries
- `project_root`: Project directory path
- `config_files`: Configuration file paths

### Environment Requirements

Tests expect the following services to be available:
- PostgreSQL: `localhost:5432`
- PGAdmin: `localhost:8080`
- Superset: `localhost:8088`

### Test Data

Tests work with whatever data is currently loaded in the database:
- Tests gracefully handle empty tables
- Some tests require data to be loaded for full validation
- Tests validate schema structure regardless of data presence

## Adding New Tests

### Test File Naming
- Follow pattern: `test_*.py`
- Use descriptive names: `test_feature_name.py`

### Test Class Organization
```python
class TestFeatureName:
    """Test specific feature functionality"""

    def test_specific_behavior(self):
        """Test specific behavior with clear description"""
        # Test implementation
```

### Database Connection Pattern
```python
def test_database_feature(self, postgres_connection):
    cursor = postgres_connection.cursor()
    cursor.execute("SELECT * FROM table;")
    result = cursor.fetchall()
    assert len(result) >= 0
```

### Skipping Tests for Missing Services
```python
try:
    # Test code that requires service
    pass
except ServiceNotAvailableError:
    pytest.skip("Service not running")
```

## Continuous Integration

These tests are designed to:
- Validate Docker environment setup
- Ensure data integrity after changes
- Verify configuration consistency
- Test service connectivity

Perfect for integration into CI/CD pipelines to ensure environment reliability.