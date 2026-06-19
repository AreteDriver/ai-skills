---
name: postmortem
description: Incident Postmortem Template
lifecycle: experimental
---

# /postmortem - Incident Postmortem Template

Create blameless postmortem reports for incidents.

## Usage
```
/postmortem                      # Generate template
/postmortem "database outage"    # Pre-fill incident type
/postmortem --severity high      # Set severity level
```

## What This Skill Does

1. **Structure Report** - Standard postmortem format
2. **Guide Analysis** - 5 Whys, timeline, contributing factors
3. **Track Action Items** - Preventive measures
4. **Facilitate Learning** - Blameless retrospective
5. **Document History** - Searchable incident record

## Postmortem Template

```markdown
# Incident Postmortem: [Incident Title]

**Date**: YYYY-MM-DD
**Author**: [Name]
**Status**: Draft | In Review | Final
**Severity**: Critical | High | Medium | Low

---

## Executive Summary

One paragraph summary: what happened, impact, resolution, key learnings.

---

## Incident Details

| Field | Value |
|-------|-------|
| **Incident ID** | INC-XXXX |
| **Start Time** | YYYY-MM-DD HH:MM UTC |
| **Detection Time** | YYYY-MM-DD HH:MM UTC |
| **Resolution Time** | YYYY-MM-DD HH:MM UTC |
| **Duration** | X hours Y minutes |
| **Time to Detect** | X minutes |
| **Time to Resolve** | X hours |

---

## Impact

### User Impact
- Number of users affected: X
- Percentage of traffic affected: X%
- Features unavailable: [list]

### Business Impact
- Revenue impact: $X (if applicable)
- SLA breach: Yes/No
- Customer complaints: X

### Data Impact
- Data loss: Yes/No
- Data corruption: Yes/No
- Details: [if applicable]

---

## Timeline

All times in UTC.

| Time | Event |
|------|-------|
| HH:MM | [First anomaly in metrics] |
| HH:MM | [Alert triggered] |
| HH:MM | [On-call paged] |
| HH:MM | [Investigation started] |
| HH:MM | [Root cause identified] |
| HH:MM | [Fix deployed] |
| HH:MM | [Service restored] |
| HH:MM | [Incident closed] |

---

## Root Cause Analysis

### What Happened
Detailed technical description of what went wrong.

### 5 Whys Analysis

1. **Why did the service go down?**
   → [Answer]

2. **Why did [Answer 1] happen?**
   → [Answer]

3. **Why did [Answer 2] happen?**
   → [Answer]

4. **Why did [Answer 3] happen?**
   → [Answer]

5. **Why did [Answer 4] happen?**
   → [Root cause]

### Contributing Factors
- Factor 1: [description]
- Factor 2: [description]
- Factor 3: [description]

---

## Detection

### How Was It Detected?
- [ ] Automated alert
- [ ] Customer report
- [ ] Internal user report
- [ ] Routine check

### Detection Gap Analysis
- What alerts existed? Did they fire?
- What alerts should have existed?
- How could we detect this faster?

---

## Response

### What Went Well
- [Positive aspect 1]
- [Positive aspect 2]

### What Could Be Improved
- [Improvement area 1]
- [Improvement area 2]

### Lucky Breaks
- [Things that could have been worse]

---

## Action Items

### Immediate (This Week)
| ID | Action | Owner | Due Date | Status |
|----|--------|-------|----------|--------|
| 1 | [Action] | [Name] | YYYY-MM-DD | Open |

### Short-term (This Month)
| ID | Action | Owner | Due Date | Status |
|----|--------|-------|----------|--------|
| 2 | [Action] | [Name] | YYYY-MM-DD | Open |

### Long-term (This Quarter)
| ID | Action | Owner | Due Date | Status |
|----|--------|-------|----------|--------|
| 3 | [Action] | [Name] | YYYY-MM-DD | Open |

---

## Lessons Learned

### Technical Learnings
- [Learning 1]
- [Learning 2]

### Process Learnings
- [Learning 1]
- [Learning 2]

### What We'll Do Differently
- [Change 1]
- [Change 2]

---

## Appendix

### Related Documents
- [Link to runbook]
- [Link to dashboards]
- [Link to logs]

### Communication Log
- HH:MM: [Status update posted to #channel]
- HH:MM: [Customer communication sent]

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Author | | |
| Reviewer | | |
| Approver | | |
```

## Severity Definitions

| Severity | Definition | Examples |
|----------|------------|----------|
| **Critical** | Complete service outage, data loss | Database down, security breach |
| **High** | Major feature unavailable, significant degradation | Payment processing failed |
| **Medium** | Partial degradation, workaround exists | Slow response times |
| **Low** | Minor issue, minimal user impact | UI glitch |

## Blameless Culture Guidelines

### Do
- Focus on systems and processes, not people
- Ask "what" and "how", not "who"
- Assume everyone acted with best intentions
- Look for systemic improvements
- Share learnings widely

### Don't
- Assign blame to individuals
- Use language like "should have" or "failed to"
- Hide information to protect anyone
- Skip the postmortem for "small" incidents
- Let action items go untracked

## Instructions for Claude

When /postmortem is invoked:

1. **Gather facts** - What happened, when, impact
2. **Build timeline** - Chronological events
3. **Analyze root cause** - 5 Whys, contributing factors
4. **Assess response** - What worked, what didn't
5. **Generate actions** - Preventive measures
6. **Stay blameless** - Focus on systems, not people
7. **Extract learnings** - What to do differently
8. **Format report** - Standard template
