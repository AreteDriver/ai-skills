# Security Sweep Response
## Example Output
```
for t in semgrep bandit gitleaks pip-audit; do
  command -v $t > /dev/null && echo "✓ $t" || echo "✗ $t MISSING"
done
```
