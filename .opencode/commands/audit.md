---
description: Perform a security audit
agent: security-auditor
subtask: true
---

Perform a security audit of the codebase.

## Scope

$ARGUMENTS

If no specific scope, audit:
1. All source code: `src/`
2. Dependencies
3. Configuration files

## Security Checks

### 1. Static Analysis (Bandit)
```bash
uv run bandit -r src/ -f json
```

### 2. Dependency Vulnerabilities
```bash
uv run pip-audit
```

### 3. Code Review for Security

#### Injection Vulnerabilities
- [ ] SQL injection (parameterized queries?)
- [ ] Command injection (shell=False?)
- [ ] Template injection

#### Authentication/Authorization
- [ ] Proper access controls
- [ ] No IDOR vulnerabilities
- [ ] Session handling

#### Data Protection
- [ ] No hardcoded secrets
- [ ] Sensitive data encrypted
- [ ] Proper error messages (no data leakage)

#### Input Validation
- [ ] All inputs validated
- [ ] Type checking
- [ ] Boundary checks

## OWASP Top 10 Checklist

- [ ] A01: Broken Access Control
- [ ] A02: Cryptographic Failures
- [ ] A03: Injection
- [ ] A04: Insecure Design
- [ ] A05: Security Misconfiguration
- [ ] A06: Vulnerable Components
- [ ] A07: Authentication Failures
- [ ] A08: Data Integrity Failures
- [ ] A09: Logging Failures
- [ ] A10: SSRF

## Output Format

```markdown
## Security Audit Report

### Executive Summary
[Brief overview and risk level]

### Findings Summary
| Severity | Count |
|----------|-------|
| Critical | X |
| High | X |
| Medium | X |
| Low | X |

### Critical/High Findings
[Detailed findings with remediation]

### Dependency Vulnerabilities
[List of vulnerable packages]

### Recommendations
1. [Priority action]
2. [...]

### Secure Coding Reminders
- [Specific to this codebase]
```

## Skills

Load `security` skill for detailed security guidelines and OWASP patterns.
