---
name: entity-resolver
description: Resolves entity ambiguity across document corpora. Handles fuzzy name matching, alias detection, identity consolidation, and confidence-scored entity merging. Core forensic capability for DOSSIER document intelligence and bridge to Convergent's intent graph entity layer. Use when ingesting documents with inconsistent entity references, deduplicating people/places/orgs, or building relationship graphs from messy data.
---

# Entity Resolver

Turns messy, inconsistent entity mentions into clean, consolidated identities.
"J. Smith", "John Smith", "Smith, J.", and "John A. Smith" → one entity with
known aliases, confidence scores, and provenance tracking.

## Why This Exists

NER extracts entity *mentions*. Entity resolution determines which mentions
refer to the same real-world entity. Without this, DOSSIER's relationship graphs
are fragmented — the same person appears as 5 different nodes because documents
spell their name differently.

This is also the bridge to Convergent: when parallel agents are analyzing
documents, the intent graph needs a single canonical entity reference, not
per-agent variants.

## When to Activate

- After NER extracts entities from a new document batch
- "Merge these entities" / "these are the same person"
- "Find duplicates in the entity list"
- "How confident are we that X and Y are the same person?"
- During Convergent intent resolution when agents reference the same entity differently

## Resolution Pipeline

```
Raw mentions → Normalization → Candidate generation → Scoring → Clustering → Human review
```

### Stage 1: Normalization

Transform all mentions into comparable form:

```python
def normalize(name: str) -> str:
    """
    'Dr. John A. Smith Jr.' → 'john a smith'
    'SMITH, JOHN' → 'john smith'
    'J. Smith' → 'j smith'
    """
    # Remove titles (Dr., Mr., Mrs., Ms., Prof., Hon., Sen., Rep.)
    # Remove suffixes (Jr., Sr., III, Esq., PhD, MD)
    # Remove punctuation
    # Lowercase
    # Normalize whitespace
    # Handle "Last, First" → "First Last"
```

**Place normalization:**
```python
# 'Palm Beach, FL' → 'palm beach florida'
# 'N.Y.' → 'new york'
# 'St. Louis' → 'saint louis'  (but keep original as alias)
```

**Org normalization:**
```python
# 'JP Morgan Chase & Co.' → 'jp morgan chase'
# 'JPMorgan' → 'jp morgan'  (common variant)
```

### Stage 2: Candidate Generation

For each new mention, find potential matches in existing entities.
Use multiple strategies (any match triggers scoring):

**Exact canonical match:**
```python
normalized_new == existing.canonical  # Confidence: 0.95
```

**Token overlap (Jaccard similarity):**
```python
tokens_a = set(normalized_a.split())
tokens_b = set(normalized_b.split())
jaccard = len(tokens_a & tokens_b) / len(tokens_a | tokens_b)
# Threshold: > 0.5
```

**Initial matching:**
```python
# 'j smith' matches 'john smith' if:
# - Last token matches exactly
# - First token is initial of other's first token
# Confidence: 0.70
```

**Edit distance (Levenshtein):**
```python
# 'Ghislaine Maxwell' vs 'Ghislane Maxwell' (typo)
# Threshold: distance <= 2 for names > 8 chars
# Confidence: 0.80 - (distance * 0.1)
```

**Phonetic matching (Soundex/Metaphone):**
```python
# 'Smith' and 'Smyth' have same Soundex code
# Useful for OCR errors and transliteration variants
# Confidence: 0.60
```

### Stage 3: Scoring

Each candidate pair gets a composite confidence score:

```python
score = weighted_average([
    (exact_match, 0.95, 3.0),      # Highest weight
    (jaccard_sim, jaccard, 2.0),
    (initial_match, 0.70, 1.5),
    (edit_distance_score, ed, 1.0),
    (phonetic_match, 0.60, 0.5),
])

# Context boosters (increase confidence):
# +0.10 if entities co-occur in same document
# +0.15 if entities appear in same role (both witnesses, both defendants)
# +0.10 if entity types match (both person, both org)

# Context reducers (decrease confidence):
# -0.20 if entities appear in same sentence as distinct references
#        ("John Smith and J. Smith met" → probably different people)
# -0.15 if different entity types (person vs org)
```

### Stage 4: Clustering

Group entity mentions into identity clusters:

```
AUTO-MERGE:    score >= 0.85 → merge automatically
SUGGEST-MERGE: 0.60 <= score < 0.85 → flag for human review
NO-MERGE:      score < 0.60 → keep separate
```

When merging:
- Pick the most complete name as canonical ("John A. Smith" over "J. Smith")
- Preserve all variants as aliases
- Track provenance (which document first introduced each alias)
- Keep the highest entity count across documents

### Stage 5: Human Review Queue

Uncertain merges go to a review queue:

```
ENTITY RESOLUTION — Review Queue (7 items)
═══════════════════════════════════════════

1. [0.78] "J. Epstein" ↔ "Jeffrey Epstein"
   Evidence: Same document (doc #42), both tagged as person
   Action: [Merge] [Keep Separate] [Skip]

2. [0.62] "Palm Beach" ↔ "Palm Beach County"
   Evidence: Different documents, both places
   Action: [Merge] [Keep Separate] [Skip]

3. [0.71] "Maxwell" ↔ "Ghislaine Maxwell"
   Evidence: 3 co-occurrences, "Maxwell" always near "Ghislaine" in context
   Action: [Merge] [Keep Separate] [Skip]
```

## Database Schema

```sql
-- Extend existing entities table with resolution metadata
ALTER TABLE entities ADD COLUMN resolved_to INTEGER REFERENCES entities(id);
ALTER TABLE entities ADD COLUMN resolution_confidence REAL;
ALTER TABLE entities ADD COLUMN resolution_method TEXT;  -- auto/manual/suggested

-- Alias tracking
CREATE TABLE IF NOT EXISTS entity_aliases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id   INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    alias       TEXT NOT NULL,
    normalized  TEXT NOT NULL,
    source_doc  INTEGER REFERENCES documents(id),
    first_seen  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resolution audit log
CREATE TABLE IF NOT EXISTS resolution_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id   INTEGER NOT NULL REFERENCES entities(id),
    target_id   INTEGER NOT NULL REFERENCES entities(id),
    action      TEXT NOT NULL,  -- merge/reject/split
    confidence  REAL,
    method      TEXT,           -- auto/manual
    reason      TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Review queue
CREATE TABLE IF NOT EXISTS resolution_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_a_id INTEGER NOT NULL REFERENCES entities(id),
    entity_b_id INTEGER NOT NULL REFERENCES entities(id),
    confidence  REAL NOT NULL,
    evidence    TEXT,           -- JSON: co-occurrence count, shared docs, etc.
    status      TEXT DEFAULT 'pending',  -- pending/approved/rejected
    reviewed_at TIMESTAMP
);
```

## API Endpoints

```
POST   /api/entities/resolve          Run resolution on all unresolved entities
POST   /api/entities/resolve/{id}     Resolve a specific entity against corpus
GET    /api/entities/duplicates        Get suspected duplicates above threshold
GET    /api/entities/queue             Get human review queue
POST   /api/entities/merge             Manually merge two entities
POST   /api/entities/split             Split a previously merged entity
GET    /api/entities/{id}/aliases      Get all known aliases for an entity
```

## Convergent Integration

When used with Convergent's intent graph:

```python
# Agent A publishes intent with entity "J. Smith"
# Agent B publishes intent with entity "John Smith"
# Entity resolver runs as part of intent resolution:

class EntityAwareIntentResolver(IntentResolver):
    def resolve(self, my_intent, graph):
        # Standard intent resolution
        resolved = super().resolve(my_intent, graph)

        # Entity resolution layer
        for entity in my_intent.entities:
            canonical = self.entity_resolver.find_canonical(entity)
            if canonical and canonical != entity:
                resolved.adjustments.append(
                    AdoptCanonicalEntity(original=entity, canonical=canonical)
                )

        return resolved
```

This ensures all agents converge on the same entity identities without
explicit communication — exactly the ambient awareness pattern.

## Constraints

- **Never auto-merge below 0.85** — uncertain merges always go to review queue
- **Always preserve aliases** — merging doesn't delete the original name
- **Audit trail required** — every merge/split is logged with reason
- **Reversible** — any merge can be split if later evidence contradicts it
- **OCR-aware** — expect and handle common OCR errors (rn→m, l→1, O→0)
- **Type-safe** — never merge across entity types (person ↔ org) without explicit override
