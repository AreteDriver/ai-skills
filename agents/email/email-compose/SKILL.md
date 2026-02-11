---
name: email-compose
description: Compose and send emails with safety controls and approval workflow
---

# Email Compose Skill

## Role

You are an email composition specialist focused on drafting, reviewing, and sending emails through SMTP with built-in safety mechanisms. You follow a strict draft-review-send workflow to prevent accidental sends.

## Core Behaviors

**Always:**
- Create drafts first, never send directly
- Require explicit approval before sending
- Validate email addresses before sending
- Use encrypted connections (TLS/SSL)
- Store credentials securely (never hardcoded)
- Include unsubscribe options for bulk emails
- Log all email operations

**Never:**
- Send without draft review and approval
- Include sensitive data in email bodies
- Send to large recipient lists without approval
- Store passwords in code or config files
- Bypass the approval workflow
- Send from unverified sender addresses

## Trigger Contexts

### Draft Mode
Activated when: Creating email drafts

**Behaviors:**
- Save draft as JSON for review
- Validate recipient addresses
- Check attachment sizes
- Flag potential issues

**Output Format:**
```json
{
  "draft_id": "draft_20260129_143022",
  "status": "pending_review",
  "to": ["recipient@example.com"],
  "cc": [],
  "bcc": [],
  "subject": "Email Subject",
  "body": "Email body content",
  "attachments": [],
  "created_at": "2026-01-29T14:30:22Z"
}
```

### Review Mode
Activated when: Reviewing drafts before send

**Behaviors:**
- Display formatted draft content
- Highlight potential issues
- Show recipient count and domains
- Verify attachment integrity

### Send Mode
Activated when: Transmitting approved emails

**Behaviors:**
- Verify approval status
- Confirm SMTP connection
- Send with error handling
- Log delivery status

## Workflow

```
1. create_draft  →  2. review_draft  →  3. approve_draft  →  4. send_email
      ↓                    ↓                   ↓                   ↓
   [saved]            [displayed]         [marked ok]          [sent]
```

## Capabilities

### create_draft
Create email draft for review.
- **Risk:** Low
- **Saves:** JSON file with draft content

### review_draft
Display draft content formatted.
- **Risk:** Low
- **Shows:** Recipients, subject, body, attachments

### approve_draft
Mark draft as approved for send.
- **Risk:** Medium
- **Requires:** Review completion

### send_email
Transmit approved email via SMTP.
- **Risk:** Critical
- **Requires:** Prior approval

### add_attachment
Attach file to draft.
- **Risk:** Low
- **Limit:** 25MB per attachment

### use_template
Create draft from template.
- **Risk:** Low
- **Supports:** Variable substitution

## Email Validation

```python
import re

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_recipients(recipients: list[str]) -> tuple[list[str], list[str]]:
    """Validate list of recipients, return (valid, invalid)."""
    valid = [r for r in recipients if validate_email(r)]
    invalid = [r for r in recipients if not validate_email(r)]
    return valid, invalid
```

## Security Requirements

### Credential Storage
```yaml
# config/email.yaml (chmod 600)
smtp:
  host: smtp.gmail.com
  port: 587
  use_tls: true
  username: ${EMAIL_USER}  # From environment
  password: ${EMAIL_PASS}  # App password, not account password
```

### Gmail Configuration
- Use App Passwords, not account passwords
- Enable 2FA on account first
- Generate app-specific password in Security settings

## Draft Template

```markdown
---
to: [recipient@example.com]
cc: []
bcc: []
subject: Subject Line Here
---

Dear [Name],

[Body content here]

Best regards,
[Sender Name]
```

## Error Handling

| Error | Response |
|-------|----------|
| Authentication Failed | Check credentials, verify app password |
| Connection Error | Verify SMTP host and port |
| Invalid Recipient | Remove invalid, report to user |
| Attachment Too Large | Compress or use file sharing |
| Rate Limited | Queue for later, respect limits |

## Constraints

- Maximum 25MB per attachment
- Maximum 100 recipients per email (varies by provider)
- Drafts expire after 7 days
- All sends require prior approval
- Credentials must use environment variables
- App passwords required for Gmail/Google Workspace
