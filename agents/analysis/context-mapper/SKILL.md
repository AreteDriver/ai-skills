---
name: context-mapper
description: Pre-execution mapping of codebases, document collections, or problem spaces. Runs BEFORE any Gorgon workflow to give all agents shared situational awareness. Produces a structured context map covering architecture, conventions, dependencies, boundaries, and domain vocabulary. Eliminates the cold-start problem where every agent wastes tokens rediscovering the same project structure. Inspired by Blitzy's pre-execution analysis phase.
---

# Context Mapper

Map the terrain before sending in the agents. This skill runs as Stage 0 of any
Gorgon workflow, producing a structured context document that all downstream
agents consume. The result: agents start with shared understanding instead of
independently rediscovering the same project structure.

## Why This Exists

Without context mapping, every agent in a Gorgon workflow starts cold:
- Builder agent reads the file tree to understand the project
- Tester agent reads the file tree to find test conventions
- Reviewer agent reads the file tree to understand architecture

That's 3x the same discovery work, burning tokens and time. Context Mapper
does this once, producing a structured map all agents share.

This is also critical for DOSSIER: before analyzing a document corpus, you need
to understand what you're looking at — how many documents, what types, what time
range, what entities are already known.

## When to Activate

- Before any Gorgon workflow execution (automatic Stage 0)
- "Map this codebase" / "What are we working with?"
- "Analyze this document collection before we start"
- When an agent reports confusion about project structure
- When switching between projects in a multi-repo workflow

## Operating Modes

| Mode | Input | Output |
|------|-------|--------|
| **Codebase** | Repository path | `context-map.json` with architecture, conventions, deps |
| **Corpus** | Document directory | `corpus-map.json` with doc types, entities, date range |
| **Problem** | Task description + repo | `problem-map.json` with affected files, interfaces, risks |

## Codebase Mapping

### What to Capture

**1. Project Identity**
```json
{
  "name": "dossier",
  "language": "python",
  "framework": "fastapi",
  "version": "0.1.0",
  "description": "Document intelligence system",
  "entry_points": ["python -m dossier serve", "python -m dossier ingest"]
}
```

**2. Architecture Map**
```json
{
  "structure": "modular",
  "layers": [
    {"name": "api", "path": "dossier/api/", "purpose": "FastAPI REST endpoints"},
    {"name": "core", "path": "dossier/core/", "purpose": "NER engine, classifiers"},
    {"name": "db", "path": "dossier/db/", "purpose": "SQLite schema, FTS5 search"},
    {"name": "ingestion", "path": "dossier/ingestion/", "purpose": "PDF/OCR text extraction"},
    {"name": "forensics", "path": "dossier/forensics/", "purpose": "Timeline, provenance, anomaly"}
  ],
  "data_flow": "upload → extractor → NER → database → API → frontend"
}
```

**3. Conventions Detected**
```json
{
  "naming": "snake_case (Python standard)",
  "test_pattern": "tests/test_{module}.py",
  "config_style": "environment variables via os.environ",
  "imports": "absolute (from dossier.core.ner import ...)",
  "docstrings": "Google style, present on ~60% of public functions",
  "type_hints": "partial (function signatures, not variables)"
}
```

**4. Dependencies & Interfaces**
```json
{
  "external_deps": [
    {"name": "fastapi", "version": ">=0.100.0", "role": "web framework"},
    {"name": "pdfplumber", "version": ">=0.10.0", "role": "PDF text extraction"},
    {"name": "python-dateutil", "version": ">=2.8.0", "role": "date parsing"}
  ],
  "internal_interfaces": [
    {"from": "ingestion.pipeline", "to": "core.ner", "type": "function call"},
    {"from": "api.server", "to": "db.database", "type": "context manager"},
    {"from": "forensics.timeline", "to": "db.database", "type": "direct SQL"}
  ]
}
```

**5. Boundaries & Constraints**
```json
{
  "do_not_modify": [
    "dossier/db/database.py schema (migration required)",
    "dossier/static/index.html (generated, edit source instead)"
  ],
  "known_issues": [
    "NER uses regex, not spaCy — fast but limited",
    "No authentication on API endpoints",
    "SQLite single-writer limitation for concurrent ingestion"
  ],
  "test_coverage": {
    "has_tests": true,
    "framework": "pytest",
    "coverage_estimate": "~40% (forensics well-tested, API untested)"
  }
}
```

**6. Domain Vocabulary**
```json
{
  "terms": {
    "entity": "A person, place, or organization extracted from document text",
    "ingestion": "The process of importing and processing a document into the system",
    "canonical": "The normalized/deduplicated form of an entity name",
    "corpus": "The full collection of documents in the system",
    "FTS5": "SQLite full-text search extension used for keyword search"
  }
}
```

## Corpus Mapping (DOSSIER Mode)

For document collections, map the terrain differently:

```json
{
  "corpus_name": "FOIA Release Batch 2024-03",
  "total_documents": 847,
  "total_pages_estimated": 3200,
  "file_types": {"pdf": 612, "txt": 180, "html": 55},
  "date_range": {"earliest": "1998-03-15", "latest": "2019-08-10"},
  "categories_detected": {
    "deposition": 42,
    "correspondence": 215,
    "flight_log": 18,
    "legal_filing": 89,
    "report": 134,
    "uncategorized": 349
  },
  "top_entities_preview": [
    {"name": "Jeffrey Epstein", "mentions": 1247, "type": "person"},
    {"name": "Palm Beach", "mentions": 389, "type": "place"}
  ],
  "languages_detected": ["en"],
  "ocr_required_estimate": 180,
  "quality_flags": {
    "low_quality_scans": 23,
    "empty_documents": 5,
    "duplicates_detected": 12
  }
}
```

## Problem Mapping

When a specific task is requested, map the problem space:

```json
{
  "task": "Add entity resolution to DOSSIER",
  "affected_files": [
    "dossier/core/ner.py (entity extraction output)",
    "dossier/db/database.py (schema changes needed)",
    "dossier/api/server.py (new endpoints)"
  ],
  "interfaces_touched": [
    "entities table schema",
    "document_entities junction table",
    "NER output format"
  ],
  "risks": [
    "Schema migration needed — existing data must be preserved",
    "Entity merge could break existing document-entity links",
    "Performance: fuzzy matching on large entity sets could be slow"
  ],
  "suggested_approach": "Add new tables alongside existing, migrate gradually",
  "estimated_scope": "medium (2-4 hours, touches 3 modules)"
}
```

## How Agents Consume the Context Map

The context map is injected into every agent's system prompt at workflow start:

```yaml
# In Gorgon workflow
agents:
  - role: context_mapper
    task: "Map the codebase/corpus before work begins"
    output: context-map.json
    checkpoint: true

  - role: builder
    task: "Implement the feature"
    depends_on: [context_mapper]
    context: "{{ agents.context_mapper.output }}"  # Injected automatically
```

Agents should reference the context map instead of rediscovering:
- "Per context map, tests follow `tests/test_{module}.py` pattern"
- "Per context map, database access uses `get_db()` context manager"
- "Per context map, do not modify the schema directly — migration required"

## Staleness Detection

Context maps go stale. Detect and refresh when:
- Any file in the mapped project has a newer mtime than the map
- Git log shows commits since map creation
- Agent reports "file not found" or "unexpected structure"

```bash
# Quick staleness check
map_time=$(stat -c %Y context-map.json)
newest_file=$(find . -name "*.py" -newer context-map.json | head -1)
if [ -n "$newest_file" ]; then
    echo "STALE: context map needs refresh"
fi
```

## Gorgon Workflow Integration

```yaml
workflow:
  name: any_workflow_with_context
  agents:
    - role: context_mapper
      agent_ref: skills/context-mapper/SKILL.md
      task: "Map the project before work begins"
      budget: { max_tokens: 1500 }
      timeout: 60
      output: context-map.json
      checkpoint: true
      # Reuse cached map if less than 1 hour old
      cache: { ttl: 3600, key: "{{ inputs.repo_path }}" }

    # All subsequent agents receive context automatically
    - role: builder
      depends_on: [context_mapper]
      context_inject: "{{ agents.context_mapper.output }}"
```

## Constraints

- **Read-only** — context mapping never modifies the project
- **Bounded** — cap file tree scanning at 500 files, sample for larger projects
- **Cacheable** — reuse maps when project hasn't changed
- **Language-aware** — detect conventions per language, don't assume Python patterns for Rust
- **Honest about gaps** — if a section can't be determined, say "unknown" rather than guess
