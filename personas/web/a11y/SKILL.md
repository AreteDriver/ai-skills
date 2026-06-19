---
name: a11y
description: Accessibility Checklist
lifecycle: experimental
---

# /a11y - Accessibility Checklist

Web accessibility audit and guidelines (WCAG compliance).

## Usage
```
/a11y                            # General checklist
/a11y path/to/component.tsx      # Audit specific component
/a11y --level AA                 # WCAG level (A, AA, AAA)
/a11y --fix                      # Suggest fixes
```

## What This Skill Does

1. **Audit Components** - Check for a11y issues
2. **Apply WCAG** - Web Content Accessibility Guidelines
3. **Suggest Fixes** - Code changes for compliance
4. **Test Guidance** - How to verify accessibility
5. **Document Requirements** - Per-component needs

## Accessibility Audit Report

```markdown
# Accessibility Audit: [Component/Page]

## Summary
| Category | Status | Issues |
|----------|--------|--------|
| Perceivable | ⚠️ | 3 |
| Operable | ✅ | 0 |
| Understandable | ⚠️ | 1 |
| Robust | ✅ | 0 |

**WCAG Level**: AA
**Overall**: Needs Improvement

---

## Issues Found

### Critical (Must Fix)

#### 1. Missing alt text on images
**WCAG**: 1.1.1 Non-text Content (Level A)
**Location**: `ProductCard.tsx:45`

```tsx
// Current (inaccessible)
<img src={product.image} />

// Fixed
<img src={product.image} alt={product.name} />
```

### Major (Should Fix)

#### 2. Low color contrast
**WCAG**: 1.4.3 Contrast (Minimum) (Level AA)
**Location**: `Button.tsx:12`

Current contrast ratio: 3.5:1 (requires 4.5:1)

```css
/* Current */
color: #888;
background: #fff;

/* Fixed */
color: #595959;
background: #fff;
```

### Minor (Nice to Have)

#### 3. Missing skip link
**WCAG**: 2.4.1 Bypass Blocks (Level A)

Add skip navigation link for keyboard users.

```tsx
<a href="#main-content" className="skip-link">
  Skip to main content
</a>
```

---

## Checklist by Category

### Perceivable
- [x] All images have alt text
- [ ] Videos have captions
- [x] Color is not the only indicator
- [ ] Sufficient color contrast (4.5:1)

### Operable
- [x] All functionality keyboard accessible
- [x] No keyboard traps
- [x] Focus indicators visible
- [x] Skip links provided

### Understandable
- [x] Language declared
- [ ] Error messages helpful
- [x] Labels on form inputs
- [x] Consistent navigation

### Robust
- [x] Valid HTML
- [x] ARIA used correctly
- [x] Works with assistive tech
```

## WCAG Quick Reference

### Level A (Minimum)
Must have for basic accessibility.

| Criterion | Requirement |
|-----------|-------------|
| 1.1.1 | Alt text for images |
| 1.3.1 | Info and relationships (semantic HTML) |
| 1.4.1 | Color not sole indicator |
| 2.1.1 | Keyboard accessible |
| 2.1.2 | No keyboard trap |
| 2.4.1 | Skip navigation |
| 3.1.1 | Language of page |
| 4.1.1 | Valid HTML |
| 4.1.2 | Name, role, value |

### Level AA (Standard)
Required for most compliance needs.

| Criterion | Requirement |
|-----------|-------------|
| 1.4.3 | Contrast ratio 4.5:1 (text) |
| 1.4.4 | Text resizable to 200% |
| 1.4.5 | Images of text avoided |
| 2.4.5 | Multiple ways to find pages |
| 2.4.6 | Descriptive headings/labels |
| 2.4.7 | Visible focus indicator |
| 3.2.3 | Consistent navigation |
| 3.2.4 | Consistent identification |

### Level AAA (Enhanced)
Highest level, not always achievable.

| Criterion | Requirement |
|-----------|-------------|
| 1.4.6 | Contrast ratio 7:1 |
| 1.4.8 | Visual presentation options |
| 2.1.3 | Keyboard (no exceptions) |
| 2.4.9 | Link purpose (link only) |

## Common Fixes

### Images
```tsx
// Informative image
<img src="chart.png" alt="Sales increased 25% in Q4" />

// Decorative image
<img src="decoration.png" alt="" role="presentation" />

// Complex image
<figure>
  <img src="diagram.png" alt="System architecture" />
  <figcaption>
    Detailed description of the system architecture...
  </figcaption>
</figure>
```

### Forms
```tsx
// Labeled input
<label htmlFor="email">Email address</label>
<input id="email" type="email" aria-describedby="email-hint" />
<span id="email-hint">We'll never share your email</span>

// Error state
<input
  aria-invalid="true"
  aria-describedby="email-error"
/>
<span id="email-error" role="alert">
  Please enter a valid email
</span>
```

### Buttons
```tsx
// Icon button needs label
<button aria-label="Close dialog">
  <CloseIcon />
</button>

// Toggle button
<button
  aria-pressed={isActive}
  onClick={toggle}
>
  Dark mode
</button>
```

### Navigation
```tsx
// Landmark regions
<header role="banner">...</header>
<nav role="navigation" aria-label="Main">...</nav>
<main role="main" id="main-content">...</main>
<footer role="contentinfo">...</footer>

// Skip link
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

### ARIA Patterns
```tsx
// Tab panel
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="panel1">
    Tab 1
  </button>
</div>
<div role="tabpanel" id="panel1">Content</div>

// Modal dialog
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
>
  <h2 id="dialog-title">Dialog Title</h2>
</div>

// Live region for updates
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>
```

## Testing Tools

### Automated
- axe DevTools (browser extension)
- Lighthouse (Chrome DevTools)
- WAVE (web tool)
- eslint-plugin-jsx-a11y

### Manual Testing
- Keyboard navigation (Tab, Enter, Escape)
- Screen reader (NVDA, VoiceOver)
- Zoom to 200%
- High contrast mode

### Commands
```bash
# axe-core CLI
npx axe https://example.com

# Pa11y
npx pa11y https://example.com

# Lighthouse
npx lighthouse https://example.com --only-categories=accessibility
```

## Instructions for Claude

When /a11y is invoked:

1. **Identify scope** - Component, page, or full site
2. **Check WCAG level** - A, AA, or AAA target
3. **Audit perceivable** - Alt text, contrast, color
4. **Audit operable** - Keyboard, focus, timing
5. **Audit understandable** - Labels, errors, consistency
6. **Audit robust** - Valid HTML, ARIA usage
7. **Prioritize issues** - Critical, major, minor
8. **Provide fixes** - Code examples
9. **Suggest testing** - Tools and manual checks
