---
name: document-forensics
description: Investigative methodology for analyzing document collections. Defines how a forensic analyst agent reasons about documents — what to extract, what's suspicious, how to cross-reference, and how to build evidentiary chains. Covers provenance analysis (metadata forensics), anomaly detection (gaps, outliers, tampering indicators), redaction detection, and cross-document validation. The timeline module is one implementation; this skill is the overarching methodology that guides all forensic capabilities in DOSSIER.
---

# Document Forensics

The methodology skill for investigative document analysis. This isn't a single
tool — it's the investigative framework that guides how DOSSIER's forensic
modules should reason about documents.

## When to Activate

- Analyzing FOIA releases, court records, or leaked documents
- "What's suspicious about this document?"
- "Find inconsistencies across these documents"
- "Extract metadata from these PDFs"
- "What's been redacted?"
- "Build an evidentiary chain for [topic]"
- Any investigative research task in DOSSIER

## Core Principle: Documents Lie, Metadata Doesn't (Usually)

The text of a document tells you what someone wanted to communicate.
The metadata tells you the truth about when, how, and by whom it was created.
The *absence* of documents tells you what someone wanted to hide.

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

## Constraints

- **This skill guides methodology, not implementation** — specific tools (OpenCV, dateutil) live in DOSSIER's forensics modules
- **Never fabricate evidence** — if data doesn't support a conclusion, say so
- **Confidence scoring is mandatory** — every finding needs a confidence level
- **Human-in-the-loop for conclusions** — automated analysis produces findings, human produces conclusions
- **Preserve chain of custody** — track which document, page, and line produced each finding
- **Anomaly ≠ guilt** — suspicious metadata could have innocent explanations. Flag, don't conclude.
