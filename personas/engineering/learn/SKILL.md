---
name: learn
description: Learning Resources & Path
---

# /learn - Learning Resources & Path

Provide learning resources and study paths for topics.

## Usage
```
/learn rust                      # Learning path for Rust
/learn "async python"            # Resources for async Python
/learn --level beginner          # Beginner resources
/learn --project                 # Project-based learning
```

## What This Skill Does

1. **Assess Topic** - Scope, prerequisites
2. **Find Resources** - Official docs, tutorials, courses
3. **Create Path** - Ordered learning sequence
4. **Suggest Projects** - Hands-on practice
5. **Track Progress** - Milestones to check off

## Learning Path Format

```markdown
# Learning Path: [Topic]

## Overview
What you'll learn and why it matters.

## Prerequisites
- [ ] Prerequisite 1
- [ ] Prerequisite 2

## Learning Path

### Phase 1: Fundamentals (Week 1-2)

#### Goals
- Understand basic concepts
- Set up development environment
- Write first program

#### Resources
1. **Official Tutorial** (Free)
   - [Link](url)
   - Time: 4 hours
   - Covers: Basics

2. **Video Course** (Free)
   - [Link](url)
   - Time: 2 hours
   - Covers: Getting started

#### Practice
- [ ] Complete official tutorial
- [ ] Build "Hello World"
- [ ] Solve 5 easy exercises on [Platform]

#### Milestone
Can create and run a simple program.

---

### Phase 2: Core Concepts (Week 3-4)

#### Goals
- Master core language features
- Understand common patterns
- Build small projects

#### Resources
...

#### Practice Projects
1. **Project Name**
   - Description
   - Concepts practiced
   - Estimated time

---

### Phase 3: Advanced Topics (Week 5-8)

...

## Recommended Books
| Book | Level | Focus |
|------|-------|-------|
| Title 1 | Beginner | Fundamentals |
| Title 2 | Intermediate | Patterns |

## Communities
- Discord: [Server Name](url)
- Reddit: r/topic
- Forum: [Name](url)

## Progress Tracker
- [ ] Phase 1 complete
- [ ] First project built
- [ ] Phase 2 complete
- [ ] Intermediate project
- [ ] Phase 3 complete
- [ ] Advanced project
```

## Learning Paths by Topic

### Rust
```markdown
### Phase 1: Basics
- The Rust Book (free, official)
- Rustlings exercises
- "Hello World" CLI

### Phase 2: Ownership & Types
- Rust by Example
- Exercism Rust track
- Build a CLI tool

### Phase 3: Advanced
- Async Rust
- Unsafe Rust
- Build a web service
```

### Python Async
```markdown
### Phase 1: Fundamentals
- Python docs: asyncio
- Real Python async tutorial
- Simple async scripts

### Phase 2: Patterns
- aiohttp for HTTP
- asyncio patterns
- Build async web scraper

### Phase 3: Production
- FastAPI/Starlette
- Testing async code
- Build async API
```

### Game Development
```markdown
### Phase 1: Basics
- Choose engine (Godot/Unity/Bevy)
- Official tutorials
- Clone simple game (Pong)

### Phase 2: Core Skills
- Physics, input, rendering
- Game loop patterns
- Build platformer

### Phase 3: Polish
- UI, audio, juice
- Optimization
- Complete small game
```

## Resource Quality Indicators

| Indicator | Meaning |
|-----------|---------|
| Official | From language/framework creators |
| Free | No cost |
| Interactive | Hands-on exercises |
| Video | Video format |
| Book | Book format |
| Updated | Recently updated |

## Project Ideas by Level

### Beginner
- CLI calculator
- Todo list
- File organizer
- Simple game (guess number)

### Intermediate
- REST API
- Web scraper
- Chat application
- 2D game

### Advanced
- Compiler/interpreter
- Database implementation
- Distributed system
- Game engine

## Instructions for Claude

When /learn is invoked:

1. **Identify topic** - Language, framework, concept
2. **Assess level** - Beginner, intermediate, advanced
3. **Find prerequisites** - What's needed first
4. **Gather resources** - Official docs, courses, tutorials
5. **Order by difficulty** - Progressive learning
6. **Add projects** - Hands-on practice
7. **Include communities** - Where to get help
8. **Create milestones** - Checkpoints for progress
9. **Estimate time** - Realistic timeframes
