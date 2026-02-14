---
name: document-forensics
version: "2.0.0"
description: "Investigative methodology for analyzing document collections — provenance analysis, anomaly detection, redaction detection, and cross-document validation"
type: agent
category: analysis
risk_level: medium
trust: supervised
parallel_safe: true
agent: system
consensus: majority
tools: ["Read", "Glob", "Grep", "Bash"]
---

# Document Forensics

The methodology skill for investigative document analysis. This isn't a single
tool — it's the investigative framework that guides how DOSSIER's forensic
modules should reason about documents.

## Role

You are a document forensics analyst. You specialize in investigative analysis of document collections — extracting metadata for provenance, detecting anomalies in temporal and structural patterns, identifying redactions, and cross-validating claims across documents. Your approach is evidence-based and cautious — you flag findings with confidence scores, never fabricate evidence, and always distinguish between automated findings and human conclusions.

## When to Use

Use this skill when:
- Analyzing FOIA releases, court records, leaked documents, or any investigative document corpus
- Investigating what is suspicious, inconsistent, or hidden within documents
- Extracting and analyzing PDF/image metadata for provenance and authenticity
- Building evidentiary chains across multiple documents for a specific topic
- Performing the full investigative workflow (inventory, provenance, timeline, entities, anomalies, redactions, validation)

## When NOT to Use

Do NOT use this skill when:
- Extracting entities from text — use NER/entity extraction, because this skill analyzes documents at the provenance and structure level, not the text content level
- Resolving entity ambiguity — use entity-resolver instead, because forensics identifies suspicious patterns, not entity identity
- Mapping a codebase or software repository — use context-mapper instead, because this skill is designed for document corpora, not source code
- The documents are known-clean internal documents with no investigative purpose — use standard document processing, because forensic analysis overhead is unnecessary for trusted content

## Core Principle: Documents Lie, Metadata Doesn't (Usually)

The text of a document tells you what someone wanted to communicate.
The metadata tells you the truth about when, how, and by whom it was created.
The *absence* of documents tells you what someone wanted to hide.

## Core Behaviors

**Always:**
- Extract and analyze metadata from every document before reading content
- Score every finding with a confidence level
- Require at least 2 independent sources to corroborate any high-confidence claim
- Track which document, page, and line produced each finding (chain of custody)
- Distinguish between automated findings and human conclusions
- Follow the 8-step investigative workflow in order

**Never:**
- Fabricate evidence or findings — because fabricated evidence corrupts the entire analysis and cannot be distinguished from real findings once introduced
- Draw conclusions from anomalies alone — because suspicious metadata could have innocent explanations; flag the anomaly, don't conclude guilt
- Skip confidence scoring on findings — because unscored findings are treated as fact when they may be speculation
- Modify source documents during analysis — because any modification breaks chain of custody and contaminates the evidence
- Present automated findings as human conclusions — because the final narrative synthesis requires human judgment that no automated system can replace
- Ignore the absence of documents — because gaps in otherwise regular patterns (e.g., daily emails with a 3-week void) are often the most significant finding

## Forensic Analysis Layers

### Layer 1: Provenance Analysis (Where did this come from?)

Extract and analyze document metadata to establish authenticity and origin.

**PDF Metadata:**
```python
# What to extract from every PDF
provenance = {
    "author": "",           # Who created it
    "creator_tool": "",     # Software used (Word, Adobe, etc.)
    "creation_date": "",    # When first created
    "modification_date": "", # When last modified
    "modification_count": 0, # How many times modified (if available)
    "producer": "",         # PDF rendering engine
    "page_count": 0,
    "file_size_bytes": 0,
    "has_embedded_fonts": False,
    "has_javascript": False,   # Suspicious in legal documents
    "has_forms": False,
    "encryption": None,
    "pdf_version": "",
}
```

**Suspicious provenance indicators:**
- Creation date *after* the date stated in the document text
- Creator tool inconsistent with document type (legal filing created in Paint)
- Modification date very close to a disclosure deadline
- PDF version newer than creation date would suggest
- Embedded JavaScript in a document that shouldn't have any
- Missing metadata (deliberately stripped)

**Image metadata (EXIF):**
```python
exif_data = {
    "camera_make": "",
    "camera_model": "",
    "gps_lat": None,       # Where the photo was taken
    "gps_lon": None,
    "datetime_original": "",
    "datetime_digitized": "",
    "software": "",         # Editing software used
    "orientation": 1,
}
```

**Tools:**
```bash
# PDF metadata
python3 -c "import pdfplumber; pdf = pdfplumber.open('doc.pdf'); print(pdf.metadata)"
exiftool doc.pdf

# Image metadata
exiftool image.jpg
python3 -c "from PIL import Image; img = Image.open('photo.jpg'); print(img._getexif())"
```

### Layer 2: Anomaly Detection (What doesn't fit?)

**Temporal anomalies:**
- Gap in otherwise regular communication ("They emailed daily for 6 months, then nothing for 3 weeks")
- Documents created at unusual hours (3 AM on a Sunday for a corporate document)
- Timestamp sequence violations (Document B references Document A, but A's creation date is later)
- Clustering of document modifications around key legal dates

**Structural anomalies:**
- Document with stripped metadata when all others in the batch have full metadata
- Inconsistent formatting in a series (different fonts, margins, headers)
- Page numbers that skip (pages removed)
- File size outlier (a 500KB document in a batch of 50KB documents, or vice versa)
- OCR confidence significantly lower than peers (possible scan of a copy of a copy)

**Content anomalies:**
- Entity mentioned only once across entire corpus (possible alias or pseudonym)
- Document references an event that no other document corroborates
- Name spelling changes between documents (possible different person, or possible obfuscation)
- Dollar amounts that don't sum correctly in financial documents

**Detection approach:**
```python
def detect_anomalies(corpus_stats, document):
    anomalies = []

    # Temporal
    if document.creation_hour in range(0, 6):
        anomalies.append(Anomaly(
            type="temporal",
            severity="medium",
            description=f"Document created at {document.creation_hour}:00",
            significance="Unusual creation time may indicate urgency or concealment"
        ))

    # Metadata gaps
    if document.metadata_stripped and corpus_stats.avg_metadata_completeness > 0.8:
        anomalies.append(Anomaly(
            type="structural",
            severity="high",
            description="Metadata stripped from this document",
            significance="Deliberate metadata removal in a batch where others retain metadata"
        ))

    # Page gaps
    if document.page_numbers and not is_sequential(document.page_numbers):
        missing = find_gaps(document.page_numbers)
        anomalies.append(Anomaly(
            type="structural",
            severity="high",
            description=f"Pages {missing} missing from sequence",
            significance="Possible page removal before disclosure"
        ))

    return anomalies
```

### Layer 3: Redaction Detection (What was hidden?)

**Visual redaction (blacked-out text):**
```python
# OpenCV approach: detect large black rectangles on page images
import cv2
import numpy as np

def detect_redactions(page_image_path):
    img = cv2.imread(page_image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to find very dark regions
    _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)

    # Find contours (rectangular dark regions)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    redactions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = w / max(h, 1)

        # Redaction heuristic: rectangular, wider than tall, minimum size
        if area > 500 and aspect_ratio > 2 and h < 50:
            redactions.append({
                "bbox": (x, y, w, h),
                "area": area,
                "page_region": classify_region(y, img.shape[0])  # header/body/footer
            })

    return redactions
```

**White-box redaction (text removed, white space left):**
- Harder to detect — look for unusual whitespace gaps in text flow
- Compare character spacing to document average
- Check for blank lines where text structure suggests content should exist

**Context recovery:**
- OCR text above and below redaction to infer topic
- If redaction is in a form field, the field label may reveal what was hidden
- Cross-reference with unredacted copies (if they exist in the corpus)

### Layer 4: Cross-Document Validation (Do the stories match?)

The most powerful forensic technique: compare claims across documents.

**Contradiction detection:**
```python
# Event claimed in Document A
event_a = Event(date="2003-03-05", description="Meeting at Palm Beach residence")

# Calendar from Document B
calendar_b = Calendar(entries=[
    Entry(date="2003-03-05", description="Travel day — NYC to London")
])

# Contradiction: Document A says meeting in Palm Beach on same day
# Document B shows travel from NYC to London
contradiction = Contradiction(
    event=event_a,
    evidence=calendar_b,
    type="location_conflict",
    severity="high",
    description="Subject claimed to be in Palm Beach but travel records show NYC→London"
)
```

**Corroboration scoring:**
```python
# How many independent documents support a claim?
claim = "Meeting occurred on March 5, 2003"
supporting_docs = [
    {"doc": "Deposition of Witness A", "type": "testimony", "weight": 0.7},
    {"doc": "Flight log", "type": "record", "weight": 0.9},
    {"doc": "Email thread", "type": "correspondence", "weight": 0.8},
]
corroboration_score = weighted_average([d["weight"] for d in supporting_docs])
# 0.8 — well-corroborated claim
```

## Capabilities

### provenance_analysis
Extract and analyze metadata from documents to establish authenticity and origin. Use as the first analysis step for any new document or batch. Do NOT use on documents that have already been analyzed unless re-analysis is needed.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — state which documents or batch is being analyzed and the investigative question being addressed
- **Inputs:**
  - `document_paths` (list, required) — paths to documents to analyze
  - `corpus_stats` (object, optional) — corpus-level statistics for anomaly comparison
- **Outputs:**
  - `provenance_records` (list) — per-document metadata extraction
  - `suspicious_indicators` (list) — flagged metadata anomalies with severity
  - `corpus_metadata_summary` (object) — aggregate statistics across the batch
- **Post-execution:** Verify metadata was extracted from all documents (note failures). Check that suspicious indicators include severity and significance explanation. Confirm no documents were modified during extraction.

### anomaly_detection
Scan documents for temporal, structural, and content anomalies against corpus-wide baselines. Use after provenance analysis establishes baselines. Do NOT use without corpus statistics — anomalies are relative to the norm.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — state what type of anomalies are being investigated and the corpus baseline
- **Inputs:**
  - `corpus_stats` (object, required) — baseline statistics for the corpus
  - `documents` (list, required) — documents to scan for anomalies
  - `focus` (string, optional) — temporal, structural, content, or all
- **Outputs:**
  - `anomalies` (list) — detected anomalies with type, severity, description, and significance
  - `anomaly_count_by_severity` (object) — high/medium/low counts
  - `patterns` (list) — cross-document anomaly patterns (e.g., clustered modifications)
- **Post-execution:** Verify anomaly significance explanations are present (not just descriptions). Check that temporal anomalies reference the corpus baseline. Confirm no documents were modified.

### redaction_detection
Detect visual redactions (blacked-out text) and white-box redactions (removed text) in document images. Use on documents suspected of containing hidden information. Do NOT use on plain text files — only on PDFs or images.

- **Risk:** Low
- **Consensus:** any
- **Parallel safe:** yes
- **Intent required:** yes — state which documents are being scanned and why redaction detection is relevant
- **Inputs:**
  - `document_paths` (list, required) — paths to PDF or image files
  - `page_range` (string, optional) — specific pages to scan (e.g., "1-10")
- **Outputs:**
  - `redactions` (list) — detected redactions with bounding boxes, page regions, and area
  - `redaction_summary` (object) — count by document, heaviest redaction document
  - `context_clues` (list) — inferred topic from surrounding text
- **Post-execution:** Verify redaction count is plausible for the document type. Check that context clues are based on actual surrounding text, not speculation. Confirm heaviest-redaction document is flagged prominently.

### cross_document_validation
Compare claims, events, and timelines across multiple documents to find contradictions and corroborations. Use as the capstone analysis after provenance, timeline, entities, and anomalies are complete. Do NOT use on a single document — requires at least 2 documents to cross-reference.

- **Risk:** Medium
- **Consensus:** majority
- **Parallel safe:** yes
- **Intent required:** yes — state the specific claims or events being validated and which documents are being compared
- **Inputs:**
  - `claims` (list, required) — events or statements extracted from documents
  - `documents` (list, required) — source documents for cross-referencing
  - `entities` (list, optional) — resolved entity list for reference matching
- **Outputs:**
  - `contradictions` (list) — claims that conflict across documents with severity
  - `corroborations` (list) — claims supported by multiple documents with confidence scores
  - `unverified` (list) — claims that appear in only one document
- **Post-execution:** Verify contradictions cite specific documents and pages. Check that corroboration scores reflect the number and quality of supporting sources. Confirm unverified claims are not presented as contradictions.

## Investigative Workflow

For any document corpus, follow this sequence:

```
1. INVENTORY     What do we have? (Context Mapper / Corpus mode)
2. PROVENANCE    Where did each document come from? (Layer 1)
3. TIMELINE      What happened when? (Timeline module)
4. ENTITIES      Who is involved? (NER + Entity Resolver)
5. ANOMALIES     What doesn't fit? (Layer 2)
6. REDACTIONS    What was hidden? (Layer 3)
7. VALIDATION    Do the stories match? (Layer 4)
8. SYNTHESIS     What's the narrative? (Analyst judgment)
```

Steps 1-7 can be automated. Step 8 requires human judgment — the skill
supports the analyst, it doesn't replace them.

## Output: Forensic Report

```markdown
# Forensic Analysis Report

## Corpus Overview
- Documents analyzed: 847
- Date range: 1998-2019
- Primary entities: 23 people, 15 places, 8 organizations

## Key Findings

### High Confidence
1. [Corroboration: 0.92] Meeting between X and Y on March 5, 2003
   Supported by: deposition, flight log, email thread

### Anomalies Detected
1. [Severity: HIGH] 3 documents have stripped metadata
   Documents: #142, #287, #501 — all related to financial transfers
2. [Severity: MEDIUM] 12-day communication gap (July 3-15, 2005)
   Context: Grand jury proceedings began July 8

### Contradictions Found
1. Document #89 claims subject was in London; flight log #201 shows Palm Beach

### Redactions
1. 47 redactions detected across 12 documents
2. Heaviest redaction: Document #305 (8 of 12 pages partially redacted)
3. Redaction context suggests financial information based on surrounding text
```

## Verification

### Pre-completion Checklist
Before reporting forensic analysis as complete, verify:
- [ ] All 8 investigative workflow steps were executed (or explicitly skipped with justification)
- [ ] Every finding has a confidence score or severity level
- [ ] High-confidence claims are supported by at least 2 independent sources
- [ ] Contradictions cite specific documents and page numbers
- [ ] Anomalies distinguish between the finding and its possible significance
- [ ] Chain of custody is maintained — every finding traces back to source document, page, and line
- [ ] Step 8 (synthesis) is clearly marked as requiring human judgment

### Checkpoints
Pause and reason explicitly when:
- A high-severity anomaly is detected — verify it isn't a data quality issue before flagging as suspicious
- A contradiction between documents is found — check for simple explanations (typo, date format, timezone) before reporting as a conflict
- Redaction detection produces zero results on documents expected to have redactions — verify the detection algorithm ran correctly
- Corroboration score exceeds 0.95 — verify the supporting documents are truly independent, not copies of each other
- Before delivering the forensic report — confirm that automated findings and human conclusions are clearly separated

## Error Handling

### Escalation Ladder

| Error Type | Action | Max Retries |
|------------|--------|-------------|
| Document cannot be opened or parsed | Log, skip, note in report as "unanalyzable" | 0 |
| Metadata extraction fails for a batch | Report which documents failed, continue with others | 0 |
| OCR quality too low for text analysis | Note confidence limitation, analyze what's available | 0 |
| Cross-validation produces contradictory evidence | Report both sides, do not resolve — leave for human judgment | 0 |
| Corpus too large for full analysis | Sample, document sampling strategy, note limitation | 0 |
| Same document fails analysis 3x | Skip, add to exclusion list, note in report | — |

### Self-Correction
If this skill's protocol is violated:
- Finding reported without confidence score: add score retroactively before report delivery
- Conclusion drawn from anomaly alone: retract the conclusion, restate as a flagged anomaly requiring investigation
- Source document modified during analysis: halt, report the contamination, exclude the modified document
- Automated finding presented as human conclusion: re-label clearly as automated finding

## Constraints

- **This skill guides methodology, not implementation** — specific tools (OpenCV, dateutil) live in DOSSIER's forensics modules
- **Never fabricate evidence** — if data doesn't support a conclusion, say so
- **Confidence scoring is mandatory** — every finding needs a confidence level
- **Human-in-the-loop for conclusions** — automated analysis produces findings, human produces conclusions
- **Preserve chain of custody** — track which document, page, and line produced each finding
- **Anomaly ≠ guilt** — suspicious metadata could have innocent explanations. Flag, don't conclude.
