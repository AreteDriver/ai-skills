---
name: seed
description: Test Data Generation
lifecycle: experimental
---

# /seed - Test Data Generation

Generate realistic test data and fixtures.

## Usage
```
/seed User 100                   # Generate 100 User records
/seed --schema models.py         # Generate from model definitions
/seed --format json              # Output format (json, sql, csv)
/seed --realistic                # Use realistic fake data
```

## What This Skill Does

1. **Analyze Models** - Parse schema/model definitions
2. **Generate Data** - Realistic fake data
3. **Handle Relations** - Foreign keys, nested objects
4. **Output Formats** - JSON, SQL, CSV, Python fixtures
5. **Ensure Consistency** - Valid relationships

## Data Generation

### From Model Definition
```python
# Input: models.py
class User:
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool

class Order:
    id: int
    user_id: int  # FK to User
    total: Decimal
    status: str
    created_at: datetime
```

### Generated Fixtures
```python
# fixtures/users.py
from datetime import datetime
from faker import Faker

fake = Faker()

def generate_users(count: int = 10) -> list[dict]:
    """Generate fake user data."""
    users = []
    for i in range(count):
        users.append({
            "id": i + 1,
            "username": fake.user_name(),
            "email": fake.email(),
            "created_at": fake.date_time_between(
                start_date="-1y", end_date="now"
            ).isoformat(),
            "is_active": fake.boolean(chance_of_getting_true=90),
        })
    return users

def generate_orders(users: list[dict], count: int = 50) -> list[dict]:
    """Generate fake orders linked to users."""
    orders = []
    statuses = ["pending", "completed", "cancelled", "refunded"]

    for i in range(count):
        user = fake.random_element(users)
        orders.append({
            "id": i + 1,
            "user_id": user["id"],
            "total": float(fake.pydecimal(
                left_digits=3, right_digits=2, positive=True
            )),
            "status": fake.random_element(statuses),
            "created_at": fake.date_time_between(
                start_date=user["created_at"], end_date="now"
            ).isoformat(),
        })
    return orders

# Generate data
USERS = generate_users(100)
ORDERS = generate_orders(USERS, 500)
```

## Output Formats

### JSON
```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-01-15T10:30:00",
      "is_active": true
    }
  ],
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "total": 99.99,
      "status": "completed",
      "created_at": "2024-01-20T14:00:00"
    }
  ]
}
```

### SQL
```sql
INSERT INTO users (id, username, email, created_at, is_active) VALUES
(1, 'john_doe', 'john@example.com', '2024-01-15 10:30:00', true),
(2, 'jane_smith', 'jane@example.com', '2024-01-16 11:00:00', true);

INSERT INTO orders (id, user_id, total, status, created_at) VALUES
(1, 1, 99.99, 'completed', '2024-01-20 14:00:00'),
(2, 1, 49.50, 'pending', '2024-01-21 09:30:00');
```

### CSV
```csv
id,username,email,created_at,is_active
1,john_doe,john@example.com,2024-01-15T10:30:00,true
2,jane_smith,jane@example.com,2024-01-16T11:00:00,true
```

### Pytest Fixtures
```python
# conftest.py
import pytest
from fixtures.users import USERS, ORDERS

@pytest.fixture
def sample_users():
    """Provide sample user data."""
    return USERS[:10]

@pytest.fixture
def sample_user():
    """Provide a single sample user."""
    return USERS[0]

@pytest.fixture
def sample_orders(sample_users):
    """Provide orders for sample users."""
    user_ids = {u["id"] for u in sample_users}
    return [o for o in ORDERS if o["user_id"] in user_ids]

@pytest.fixture
def db_with_data(db_session, sample_users, sample_orders):
    """Database populated with sample data."""
    for user in sample_users:
        db_session.add(User(**user))
    for order in sample_orders:
        db_session.add(Order(**order))
    db_session.commit()
    return db_session
```

## Faker Providers by Type

| Field Type | Faker Method |
|------------|--------------|
| Name | `fake.name()` |
| Email | `fake.email()` |
| Username | `fake.user_name()` |
| Password | `fake.password()` |
| Phone | `fake.phone_number()` |
| Address | `fake.address()` |
| City | `fake.city()` |
| Country | `fake.country()` |
| Date | `fake.date_between()` |
| DateTime | `fake.date_time_between()` |
| Text | `fake.text()` |
| Paragraph | `fake.paragraph()` |
| UUID | `fake.uuid4()` |
| URL | `fake.url()` |
| IPv4 | `fake.ipv4()` |
| Price | `fake.pydecimal()` |
| Boolean | `fake.boolean()` |

## Domain-Specific Data

### E-commerce
```python
def generate_product():
    return {
        "id": fake.uuid4(),
        "name": fake.catch_phrase(),
        "description": fake.paragraph(),
        "price": float(fake.pydecimal(left_digits=2, right_digits=2)),
        "sku": fake.bothify("???-####"),
        "category": fake.random_element(["Electronics", "Clothing", "Books"]),
        "in_stock": fake.boolean(chance_of_getting_true=80),
    }
```

### Gaming (EVE Online)
```python
def generate_pilot():
    return {
        "id": fake.random_int(90000000, 99999999),
        "name": f"{fake.first_name()} {fake.last_name()}",
        "corporation": fake.company(),
        "security_status": round(fake.pyfloat(min_value=-10, max_value=5), 2),
        "ship_type": fake.random_element(["Rifter", "Caracal", "Dominix"]),
    }
```

## Instructions for Claude

When /seed is invoked:

1. **Parse models** - Extract fields and types
2. **Identify relationships** - Foreign keys, dependencies
3. **Choose generators** - Faker methods per field type
4. **Handle constraints** - Unique, non-null, valid ranges
5. **Generate data** - Realistic, consistent values
6. **Maintain relations** - Valid foreign keys
7. **Output format** - JSON, SQL, CSV, or Python
8. **Include fixtures** - Pytest-ready if requested
