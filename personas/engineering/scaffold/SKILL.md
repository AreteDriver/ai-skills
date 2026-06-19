---
name: scaffold
description: Project Scaffolding
lifecycle: experimental
---

# /scaffold - Project Scaffolding

Generate new project structure from templates.

## Usage
```
/scaffold python myproject       # New Python project
/scaffold rust myproject         # New Rust project
/scaffold cli myproject          # CLI application
/scaffold api myproject          # REST API project
```

## What This Skill Does

1. **Create Structure** - Directories, files
2. **Add Config** - pyproject.toml, Cargo.toml, etc.
3. **Set Up Testing** - Test directory, pytest/cargo test
4. **Add CI** - GitHub Actions workflow
5. **Create Docs** - README, CONTRIBUTING

## Python Project Structure

```
myproject/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── .gitignore
├── .env.example
├── CHANGELOG.md
├── CLAUDE.md
├── LICENSE
├── README.md
└── pyproject.toml
```

### pyproject.toml
```toml
[project]
name = "myproject"
version = "0.1.0"
description = "A brief description"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Your Name", email = "you@example.com"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
]

[project.scripts]
myproject = "myproject.main:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=myproject --cov-report=term-missing"
```

## Rust Project Structure

```
myproject/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── lib.rs
│   └── main.rs
├── tests/
│   └── integration_test.rs
├── .gitignore
├── CHANGELOG.md
├── CLAUDE.md
├── LICENSE
├── README.md
└── Cargo.toml
```

### Cargo.toml
```toml
[package]
name = "myproject"
version = "0.1.0"
edition = "2021"
authors = ["Your Name <you@example.com>"]
description = "A brief description"
license = "MIT"
repository = "https://github.com/username/myproject"
readme = "README.md"

[dependencies]

[dev-dependencies]
```

## CLI Application Template

### Python CLI (Click)
```python
# src/myproject/main.py
import click

@click.group()
@click.version_option()
def cli():
    """My CLI application."""
    pass

@cli.command()
@click.argument('name')
@click.option('--greeting', '-g', default='Hello', help='Greeting to use')
def greet(name: str, greeting: str):
    """Greet someone."""
    click.echo(f"{greeting}, {name}!")

def main():
    cli()

if __name__ == "__main__":
    main()
```

### Rust CLI (Clap)
```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "myproject")]
#[command(about = "My CLI application", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Greet someone
    Greet {
        /// Name to greet
        name: String,
        /// Greeting to use
        #[arg(short, long, default_value = "Hello")]
        greeting: String,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Greet { name, greeting } => {
            println!("{}, {}!", greeting, name);
        }
    }
}
```

## Instructions for Claude

When /scaffold is invoked:

1. **Get project name** - Valid package name
2. **Determine type** - Python, Rust, CLI, API
3. **Create directories** - src, tests, .github
4. **Write config files** - pyproject.toml/Cargo.toml
5. **Add boilerplate** - __init__.py, main.py/main.rs
6. **Set up tests** - conftest.py, sample test
7. **Add CI** - GitHub Actions workflow
8. **Create docs** - README, CHANGELOG, CLAUDE.md
9. **Add .gitignore** - Language-appropriate ignores
10. **Initialize git** - git init if requested
