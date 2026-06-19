# Accessibility Checker Response
## Example Output
```
## Component: [Name]

### Semantics
- [ ] Uses correct HTML element (button, not div)
- [ ] Has accessible name (visible label or aria-label)
- [ ] Role is appropriate (if ARIA role is used)
- [ ] States communicated (aria-expanded, aria-selected, etc.)

### Keyboard
- [ ] Focusable via Tab (or arrow keys if composite)
- [ ] Activatable via Enter/Space
- [ ] Escape closes overlays
- [ ] Focus trapped in modals
- [ ] Focus returns to trigger on close

### Visual
- [ ] Visible focus indicator (2px+ outline, 3:1 contrast)
- [ ] Sufficient color contrast
- [ ] Not relying on color alone
- [ ] Works at 200% zoom
- [ ] Respects prefers-reduced-motion

### Screen Reader
- [ ] Announces name, role, state
- [ ] Dynamic changes announced via live regions
- [ ] Error messages associated with inputs
```
