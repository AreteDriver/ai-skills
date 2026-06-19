# Security Auditor Response
## Example Output
```
# Multi-language SAST (preferred — finds dataflow + taint bugs grep misses)
command -v semgrep && semgrep --version || echo "semgrep: not installed"

# Python-specific AST scanner
command -v bandit && bandit --version || echo "bandit: not installed"

# Secret scanner (better than grep for high-entropy strings)
command -v gitleaks && gitleaks version || echo "gitleaks: not installed"

# Dep-vulnerability scanners (per ecosystem)
command -v pip-audit && pip-audit --version || echo "pip-audit: not installed"
command -v npm && npm --version || echo "npm: not installed"
command -v cargo && cargo --version || echo "cargo: not installed"

# Container scanner (if Dockerfile present)
test -f Dockerfile && (command -v trivy && trivy --version || echo "trivy: not installed")
```
