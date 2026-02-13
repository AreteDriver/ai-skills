# Docker Templates — Sandboxed Execution

The Executor agent uses these templates to generate `Dockerfile.audit` when
a repo doesn't have its own Dockerfile.

## Language Detection → Template Selection

| Indicator | Language | Template |
|-----------|----------|----------|
| `*.py`, `pyproject.toml`, `requirements.txt`, `setup.py` | Python | python-audit |
| `package.json` | Node.js | node-audit |
| `Cargo.toml` | Rust | rust-audit |
| `go.mod` | Go | go-audit |
| `*.rb`, `Gemfile` | Ruby | ruby-audit |
| Multiple languages detected | Multi | Use primary (most source files) |

## Templates

### Python

```dockerfile
FROM python:3.12-slim

# System deps for common Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Try multiple install methods
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null; \
    pip install --no-cache-dir -e ".[dev]" 2>/dev/null; \
    pip install --no-cache-dir -e . 2>/dev/null; \
    pip install --no-cache-dir . 2>/dev/null; \
    true

# Install test runner if not in deps
RUN pip install --no-cache-dir pytest 2>/dev/null; true

CMD ["python", "--version"]
```

### Node.js

```dockerfile
FROM node:20-slim

WORKDIR /app
COPY package*.json ./

RUN npm install 2>/dev/null; true

COPY . .

RUN npm run build 2>/dev/null; true

CMD ["node", "--version"]
```

### Rust

```dockerfile
FROM rust:1.77-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN cargo build --release 2>/dev/null; true

CMD ["rustc", "--version"]
```

### Go

```dockerfile
FROM golang:1.22-alpine

WORKDIR /app
COPY . .

RUN go mod download 2>/dev/null; true
RUN go build ./... 2>/dev/null; true

CMD ["go", "version"]
```

## Docker Run Parameters

All containers are executed with:

```bash
docker run \
  --rm \                          # Auto-cleanup
  --memory=512m \                 # Memory limit
  --cpus=1 \                      # CPU limit
  --network=none \                # No network (for test runs)
  --read-only \                   # Read-only root filesystem
  --tmpfs /tmp:size=100m \        # Writable tmp
  --tmpfs /app/__pycache__:size=50m \  # Python cache
  --security-opt no-new-privileges \   # No privilege escalation
  debt-audit-{repo_name} \
  {command}
```

## Timeout Enforcement

```bash
# Build: 5 minutes max
timeout 300 docker build ...

# Entry point test: 30 seconds
timeout 30 docker run ... {entrypoint} --help

# Test suite: 2 minutes
timeout 120 docker run ... pytest -v
```

## Cleanup

After every audit:
```bash
docker rmi debt-audit-{repo_name} 2>/dev/null
docker system prune -f --filter "label=debt-audit" 2>/dev/null
```
