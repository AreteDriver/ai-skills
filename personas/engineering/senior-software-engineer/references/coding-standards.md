# Coding Standards Reference

## General Principles

1. **Readability over cleverness** — Code is read far more often than it is written. Optimize for the reader.
2. **Explicit over implicit** — Make behavior obvious. Avoid magic values, hidden side effects, and implicit conversions.
3. **Fail fast** — Validate inputs early and surface errors as close to the source as possible.
4. **Single responsibility** — Each function, class, and module should have one clear purpose.
5. **DRY with judgment** — Eliminate true duplication but don't force abstractions on code that merely looks similar.

## Naming

- Use descriptive names that reveal intent: `getUserById` not `getData`
- Booleans should read as questions: `isActive`, `hasPermission`, `canEdit`
- Constants in UPPER_SNAKE_CASE
- Avoid abbreviations unless universally understood (`url`, `id`, `http`)
- Name functions as verbs, classes as nouns, interfaces as adjectives or capabilities

## Functions

- Keep functions short and focused (aim for under 30 lines)
- Limit parameters to 3-4; use an options object for more
- Avoid boolean flag parameters — split into two functions instead
- Pure functions when possible; isolate side effects
- Return early to reduce nesting

## Error Handling

- Use typed errors or error codes, not string matching
- Handle errors at the appropriate level — not too early, not too late
- Log with context: what happened, what was expected, what input caused it
- Never swallow errors silently
- Distinguish between recoverable and unrecoverable errors

## Security

- Never trust user input — validate and sanitize at system boundaries
- Use parameterized queries for database access
- Never log secrets, tokens, or passwords
- Apply principle of least privilege
- Keep dependencies updated; audit regularly

## Testing

- Test behavior, not implementation details
- Each test should be independent and deterministic
- Use descriptive test names that explain the scenario
- Cover edge cases: empty inputs, boundary values, error conditions
- Aim for meaningful coverage, not 100% line coverage

## Version Control

- Write commits that explain "why", not "what"
- Keep commits atomic — one logical change per commit
- Branch names should reflect the work: `fix/login-timeout`, `feat/export-csv`
- Review your own diff before requesting review from others
