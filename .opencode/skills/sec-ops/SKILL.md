---
name: sec-ops
description: >
  Security operations and DevSecOps practices. Covers complete CI/CD security
  pipelines with SAST (Bandit, Semgrep), DAST (OWASP ZAP), dependency scanning
  (pip-audit), secret detection (TruffleHog, Gitleaks), container scanning (Trivy),
  and STRIDE threat modeling framework.
version: "2.0"
source: mixed
related:
  - sec-basics
  - sec-owasp
  - test-ops
  - perf-ops
---

## SECOPS: SECURITY IN CI/CD

Integrate security testing into your development pipeline.

---

### Complete Security Pipeline

```yaml
# .github/workflows/security.yml
name: Security Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM

jobs:
  # Static Application Security Testing (SAST)
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        
      - name: Install dependencies
        run: uv sync --frozen
      
      - name: Bandit security scan
        run: |
          uv run bandit -r src/ \
            -ll \
            -ii \
            -f json \
            -o bandit-report.json
        continue-on-error: true
        
      - name: Semgrep scan
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/python
            p/security-audit
            p/secrets
            p/owasp-top-ten
          
      - name: Upload SAST results
        uses: actions/upload-artifact@v4
        with:
          name: sast-results
          path: |
            bandit-report.json
            semgrep-results.json

  # Dependency vulnerability scanning
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        
      - name: Install dependencies
        run: uv sync --frozen
        
      - name: pip-audit scan
        run: |
          uv run pip-audit \
            --strict \
            --desc \
            --format json \
            --output pip-audit-report.json
        continue-on-error: true
        
      - name: Safety check
        run: |
          uv run safety check \
            --full-report \
            --json > safety-report.json
        continue-on-error: true
        
      - name: Upload dependency scan results
        uses: actions/upload-artifact@v4
        with:
          name: dependency-scan-results
          path: |
            pip-audit-report.json
            safety-report.json

  # Secret scanning
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret scanning
          
      - name: TruffleHog secret scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          extra_args: --only-verified
          
      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # Container security (if using Docker)
  container-scan:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
        
      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

  # Dynamic Application Security Testing (DAST)
  dast:
    runs-on: ubuntu-latest
    needs: [sast, dependency-scan]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Start application
        run: docker compose -f docker-compose.test.yml up -d
        
      - name: Wait for application
        run: |
          for i in {1..30}; do
            curl -sf http://localhost:8000/health && break
            sleep 2
          done
          
      - name: OWASP ZAP scan
        uses: zaproxy/action-full-scan@v0.8.0
        with:
          target: 'http://localhost:8000'
          rules_file_name: '.zap/rules.tsv'
          
      - name: Stop application
        if: always()
        run: docker compose -f docker-compose.test.yml down

  # Security report aggregation
  security-report:
    runs-on: ubuntu-latest
    needs: [sast, dependency-scan, secret-scan]
    if: always()
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4
        
      - name: Generate security summary
        run: |
          echo "## Security Scan Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          
          # Parse and summarize results
          if [ -f sast-results/bandit-report.json ]; then
            HIGH=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' sast-results/bandit-report.json)
            MEDIUM=$(jq '[.results[] | select(.issue_severity == "MEDIUM")] | length' sast-results/bandit-report.json)
            echo "### Bandit SAST" >> $GITHUB_STEP_SUMMARY
            echo "- High: $HIGH" >> $GITHUB_STEP_SUMMARY
            echo "- Medium: $MEDIUM" >> $GITHUB_STEP_SUMMARY
          fi
```

---

### Security Tool Configuration

**Bandit configuration:**
```toml
# pyproject.toml
[tool.bandit]
exclude_dirs = ["tests", "scripts"]
skips = ["B101"]  # Skip assert warnings in non-test code

# Custom severity
[tool.bandit.assert_used]
skips = ["*_test.py", "test_*.py"]
```

**Semgrep rules:**
```yaml
# .semgrep/custom-rules.yml
rules:
  - id: no-hardcoded-secrets
    patterns:
      - pattern-either:
          - pattern: $KEY = "..."
          - pattern: $KEY = '...'
    pattern-filters:
      - metavariable: $KEY
        regex: (password|secret|api_key|token|credential)
    message: "Possible hardcoded secret"
    severity: ERROR
    languages: [python]
    
  - id: sql-injection-format-string
    patterns:
      - pattern: |
          $QUERY = f"... $VAR ..."
          ...
          $DB.execute($QUERY)
    message: "Possible SQL injection via f-string"
    severity: ERROR
    languages: [python]
```

---

## THREAT MODELING

Use STRIDE to identify security threats early in design.

---

### STRIDE Framework

| Threat | Definition | Example | Mitigation |
|--------|------------|---------|------------|
| **S**poofing | Pretending to be someone else | Stolen credentials | MFA, strong auth |
| **T**ampering | Modifying data/code | SQL injection | Input validation, signing |
| **R**epudiation | Denying actions | "I didn't make that purchase" | Audit logs, digital signatures |
| **I**nformation Disclosure | Exposing sensitive data | Database leak | Encryption, access control |
| **D**enial of Service | Making system unavailable | DDoS attack | Rate limiting, scaling |
| **E**levation of Privilege | Gaining unauthorized access | Admin bypass | RBAC, least privilege |

---

### Threat Modeling Process

```python
# Example: Threat model for payment feature

@dataclass
class Threat:
    category: str  # STRIDE category
    description: str
    impact: str  # HIGH, MEDIUM, LOW
    likelihood: str  # HIGH, MEDIUM, LOW
    mitigations: list[str]


PAYMENT_FEATURE_THREATS = [
    Threat(
        category="Spoofing",
        description="Attacker uses stolen credentials to make purchases",
        impact="HIGH",
        likelihood="MEDIUM",
        mitigations=[
            "Require MFA for transactions over $100",
            "Send email notification for all purchases",
            "Implement device fingerprinting",
        ],
    ),
    Threat(
        category="Tampering",
        description="Attacker modifies order total during checkout",
        impact="HIGH",
        likelihood="LOW",
        mitigations=[
            "Calculate totals server-side only",
            "Sign order data with HMAC",
            "Validate all prices against database",
        ],
    ),
    Threat(
        category="Repudiation",
        description="Customer denies making legitimate purchase",
        impact="MEDIUM",
        likelihood="MEDIUM",
        mitigations=[
            "Log all transactions with timestamps",
            "Store IP address and user agent",
            "Implement digital receipts with signatures",
        ],
    ),
    Threat(
        category="Information Disclosure",
        description="Credit card numbers exposed in logs",
        impact="HIGH",
        likelihood="MEDIUM",
        mitigations=[
            "Never log full card numbers",
            "Use tokenization (Stripe/Braintree)",
            "Encrypt sensitive data at rest",
        ],
    ),
    Threat(
        category="Denial of Service",
        description="Attacker floods checkout endpoint",
        impact="HIGH",
        likelihood="HIGH",
        mitigations=[
            "Rate limit by IP and user",
            "Use CAPTCHA for suspicious activity",
            "Implement circuit breakers",
        ],
    ),
    Threat(
        category="Elevation of Privilege",
        description="Customer accesses admin refund functionality",
        impact="HIGH",
        likelihood="LOW",
        mitigations=[
            "Strict role-based access control",
            "Validate permissions server-side",
            "Audit all admin actions",
        ],
    ),
]
```

---

### Threat Modeling Template

```markdown
# Threat Model: [Feature Name]

## Overview
Brief description of the feature and its data flows.

## Assets
- User credentials
- Payment information
- Personal data

## Trust Boundaries
1. Client <-> API Gateway
2. API Gateway <-> Application
3. Application <-> Database

## Threats (STRIDE)

### Spoofing
| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| ... | ... | ... | ... |

### Tampering
...

## Security Controls
- [ ] Input validation
- [ ] Authentication required
- [ ] Authorization checks
- [ ] Encryption at rest
- [ ] Audit logging
```

---

## Quick Reference

### Security Scanning Commands

```bash
# Dependency vulnerabilities
uv run pip-audit                     # Check installed packages
uv run pip-audit --fix               # Auto-fix where possible
uv run safety check                  # Alternative scanner

# Code security (SAST)
uv run bandit -r src/                # Security linter
uv run bandit -r src/ -ll -ii        # High severity only
uv run semgrep --config=auto src/    # Pattern-based

# Secret detection
trufflehog git file:///path/to/repo  # Find secrets in git history
gitleaks detect                      # Alternative
```

### CI/CD Security Stages

| Stage | Tools | Purpose |
|-------|-------|---------|
| **SAST** | Bandit, Semgrep | Static code analysis |
| **Dependency** | pip-audit, Safety | Vulnerability scanning |
| **Secrets** | TruffleHog, Gitleaks | Secret detection |
| **Container** | Trivy, Dockle | Image scanning |
| **DAST** | OWASP ZAP | Dynamic testing |

### STRIDE Quick Reference

| Letter | Threat | Question |
|--------|--------|----------|
| S | Spoofing | Can someone pretend to be someone else? |
| T | Tampering | Can someone modify data? |
| R | Repudiation | Can someone deny an action? |
| I | Information | Can sensitive data leak? |
| D | Denial | Can the system be made unavailable? |
| E | Elevation | Can someone gain extra privileges? |

---

## Related Skills

- `sec-basics` - Foundational security practices
- `sec-owasp` - OWASP Top 10 vulnerabilities
- `sec-api` - API security, headers, rate limiting
