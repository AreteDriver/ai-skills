---
name: docker
description: Dockerfile Generator
lifecycle: experimental
---

# /docker - Dockerfile Generator

Generate optimized Dockerfiles with best practices.

## Usage
```
/docker                  # Auto-detect and generate
/docker python           # Python application
/docker rust             # Rust application (multi-stage)
/docker --slim           # Minimal image size
```

## What This Skill Does

1. **Detect Application Type** - Language, framework, dependencies
2. **Generate Dockerfile** - Optimized for size and build speed
3. **Add .dockerignore** - Exclude unnecessary files
4. **Multi-stage Builds** - Separate build and runtime stages
5. **Security Hardening** - Non-root user, minimal base image

## Templates

### Python Application
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
RUN pip install --no-cache-dir build
COPY pyproject.toml .
COPY src/ src/
RUN python -m build --wheel

# Runtime stage
FROM python:3.11-slim

WORKDIR /app
RUN useradd --create-home --shell /bin/bash app
COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl && rm *.whl

USER app
ENTRYPOINT ["python", "-m", "myapp"]
```

### Rust Application
```dockerfile
# Build stage
FROM rust:1.75-slim as builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src/ src/

RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

RUN useradd --create-home --shell /bin/bash app
COPY --from=builder /app/target/release/myapp /usr/local/bin/

USER app
ENTRYPOINT ["myapp"]
```

### .dockerignore
```
.git/
.gitignore
.venv/
__pycache__/
*.pyc
target/
*.md
.github/
tests/
Dockerfile
.dockerignore
```

## Best Practices Applied

1. **Multi-stage builds** - Smaller final image
2. **Layer caching** - Dependencies before source code
3. **Non-root user** - Security hardening
4. **Slim base images** - Minimal attack surface
5. **.dockerignore** - Faster builds, smaller context
6. **No cache mounts** - Reproducible builds
7. **Pinned versions** - Reproducible base images

## Instructions for Claude

When /docker is invoked:

1. **Detect project type** - Check for pyproject.toml, Cargo.toml, etc.
2. **Identify entry point** - Main module or binary
3. **Use multi-stage** - Always separate build from runtime
4. **Minimize layers** - Combine RUN commands where sensible
5. **Add .dockerignore** - Create if missing
6. **Security** - Non-root user, minimal base image
7. **Document** - Add comments explaining non-obvious choices
