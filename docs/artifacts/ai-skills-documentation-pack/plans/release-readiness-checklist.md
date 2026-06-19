# Release Readiness Checklist

## Source Integrity

- [ ] Every active skill has a valid manifest
- [ ] No unexplained filesystem orphans
- [ ] Generated registry is clean
- [ ] Generated docs are clean
- [ ] Bundle catalog resolves
- [ ] No duplicate active IDs
- [ ] Digests generated

## Documentation

- [ ] README commands tested
- [ ] Counts generated
- [ ] Catalog tables generated
- [ ] Changelog complete
- [ ] Migration notes complete
- [ ] Deprecated items identified
- [ ] Support and security reporting paths documented

## Installer

- [ ] Dry-run verified
- [ ] Clean install verified
- [ ] Reinstall idempotent
- [ ] Update verified
- [ ] Rollback verified
- [ ] Uninstall preserves unknown files
- [ ] Hook opt-in verified
- [ ] Collision behavior verified
- [ ] Invalid target rejected
- [ ] Interrupted install recovery verified

## Quality

- [ ] Static contract suite passes
- [ ] Unit tests pass
- [ ] Integration matrix passes
- [ ] Behavioral eval thresholds pass
- [ ] Safety suite passes
- [ ] Adapter compatibility passes
- [ ] No unexplained regression

## Security

- [ ] Dependency audit passes
- [ ] Secret scan passes
- [ ] Hooks reviewed
- [ ] Wildcard permissions reviewed
- [ ] High/critical skills approved
- [ ] Prompt-injection tests pass
- [ ] Release provenance generated
- [ ] Checksums generated

## Release

- [ ] Version numbers consistent
- [ ] Tag signed
- [ ] Artifact smoke-tested from release archive
- [ ] Registry digest matches release
- [ ] Documentation published
- [ ] Rollback release retained
