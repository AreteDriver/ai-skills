---
name: mock
description: Test Mock & Fixture Generator
lifecycle: experimental
---

# /mock - Test Mock & Fixture Generator

Generate mock objects, fixtures, and test data.

## Usage
```
/mock ClassName                # Generate mock for class
/mock path/to/module.py        # Generate mocks for module
/mock --pytest                 # Pytest fixtures style
/mock --factory                # Factory Boy style
```

## What This Skill Does

1. **Analyze Code** - Parse classes, functions, dependencies
2. **Identify Dependencies** - External services, databases, APIs
3. **Generate Mocks** - unittest.mock or pytest-mock style
4. **Create Fixtures** - Reusable test data
5. **Add Factories** - Factory Boy patterns for models

## Output Formats

### Pytest Fixtures
```python
import pytest
from unittest.mock import Mock, MagicMock, patch

@pytest.fixture
def mock_database():
    """Mock database connection."""
    db = MagicMock()
    db.query.return_value = [{"id": 1, "name": "Test"}]
    db.insert.return_value = True
    return db

@pytest.fixture
def mock_api_client():
    """Mock external API client."""
    client = MagicMock()
    client.get.return_value = {"status": "ok", "data": []}
    client.post.return_value = {"id": 123}
    return client

@pytest.fixture
def sample_user():
    """Sample user for testing."""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00Z"
    }
```

### Factory Boy
```python
import factory
from factory import fuzzy
from myapp.models import User, Order

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    created_at = factory.Faker('date_time')

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    id = factory.Sequence(lambda n: n)
    user = factory.SubFactory(UserFactory)
    total = fuzzy.FuzzyDecimal(10.0, 1000.0)
    status = fuzzy.FuzzyChoice(['pending', 'completed', 'cancelled'])
```

### Context Managers for Patching
```python
@pytest.fixture
def mock_external_services():
    """Patch all external service calls."""
    with patch('myapp.services.api_client') as mock_api, \
         patch('myapp.services.db_client') as mock_db, \
         patch('myapp.services.cache') as mock_cache:

        mock_api.get.return_value = {"data": []}
        mock_db.query.return_value = []
        mock_cache.get.return_value = None

        yield {
            'api': mock_api,
            'db': mock_db,
            'cache': mock_cache
        }
```

## Mock Patterns

### Return Values
```python
mock.method.return_value = "result"
mock.method.side_effect = [1, 2, 3]  # Sequential returns
mock.method.side_effect = ValueError("error")  # Raise exception
```

### Assertions
```python
mock.method.assert_called_once()
mock.method.assert_called_with(arg1, arg2)
mock.method.assert_not_called()
assert mock.method.call_count == 3
```

### Async Mocks
```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_async_client():
    client = AsyncMock()
    client.fetch.return_value = {"data": []}
    return client
```

## Instructions for Claude

When /mock is invoked:

1. **Analyze target** - Class, module, or function
2. **Find dependencies** - External calls, I/O, databases
3. **Determine mock type** - Simple mock, MagicMock, AsyncMock
4. **Generate fixtures** - Pytest style by default
5. **Add sample data** - Realistic test values
6. **Include assertions** - Common assertion patterns
7. **Handle async** - Use AsyncMock where needed
8. **Write to conftest.py** - If project-wide fixtures
