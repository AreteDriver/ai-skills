# /e2e - End-to-End Test Setup

Set up end-to-end testing for applications.

## Usage
```
/e2e                     # Analyze project, suggest e2e setup
/e2e web                 # Web app e2e (Playwright/Selenium)
/e2e api                 # API e2e tests
/e2e cli                 # CLI application tests
```

## What This Skill Does

1. **Analyze Application** - Web, API, CLI, or hybrid
2. **Recommend Framework** - Playwright, Selenium, pytest, etc.
3. **Generate Setup** - Config files, dependencies
4. **Create Examples** - Sample e2e tests
5. **CI Integration** - GitHub Actions workflow

## Web App E2E (Playwright)

### Setup
```bash
pip install pytest-playwright
playwright install
```

### pytest.ini
```ini
[pytest]
testpaths = tests/e2e
asyncio_mode = auto
```

### Example Tests
```python
# tests/e2e/test_login.py
import pytest
from playwright.sync_api import Page, expect

def test_login_page_loads(page: Page):
    """Test login page renders correctly."""
    page.goto("/login")
    expect(page.locator("h1")).to_contain_text("Login")
    expect(page.locator("input[name='username']")).to_be_visible()
    expect(page.locator("input[name='password']")).to_be_visible()

def test_successful_login(page: Page):
    """Test user can log in with valid credentials."""
    page.goto("/login")
    page.fill("input[name='username']", "testuser")
    page.fill("input[name='password']", "testpass")
    page.click("button[type='submit']")

    # Should redirect to dashboard
    expect(page).to_have_url("/dashboard")
    expect(page.locator(".welcome-message")).to_contain_text("Welcome")

def test_invalid_login_shows_error(page: Page):
    """Test error message for invalid credentials."""
    page.goto("/login")
    page.fill("input[name='username']", "wrong")
    page.fill("input[name='password']", "wrong")
    page.click("button[type='submit']")

    expect(page.locator(".error-message")).to_be_visible()
```

## API E2E Tests

### Example Tests
```python
# tests/e2e/test_api.py
import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_and_get_user(client):
    """Test full user lifecycle."""
    # Create user
    create_response = client.post("/users", json={
        "username": "newuser",
        "email": "new@example.com"
    })
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Get user
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["username"] == "newuser"

    # Cleanup
    client.delete(f"/users/{user_id}")
```

## CLI E2E Tests

### Example Tests
```python
# tests/e2e/test_cli.py
import subprocess

def test_cli_help():
    """Test --help flag."""
    result = subprocess.run(
        ["myapp", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout

def test_cli_version():
    """Test --version flag."""
    result = subprocess.run(
        ["myapp", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "1." in result.stdout

def test_cli_process_file(tmp_path):
    """Test file processing."""
    # Create test file
    test_file = tmp_path / "input.txt"
    test_file.write_text("test content")

    result = subprocess.run(
        ["myapp", "process", str(test_file)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
```

## CI Integration

```yaml
# .github/workflows/e2e.yml
name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          playwright install --with-deps

      - name: Start application
        run: |
          myapp serve &
          sleep 5

      - name: Run E2E tests
        run: pytest tests/e2e -v
```

## Instructions for Claude

When /e2e is invoked:

1. **Identify app type** - Web, API, CLI, or hybrid
2. **Recommend framework** - Playwright for web, httpx for API
3. **Generate setup** - Dependencies, config files
4. **Create test structure** - Directory layout
5. **Write example tests** - Cover main user flows
6. **Add CI workflow** - GitHub Actions for e2e
7. **Include fixtures** - Test data, setup/teardown
8. **Document running** - How to run e2e locally
