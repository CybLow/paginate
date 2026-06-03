# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### For Critical Vulnerabilities

**DO NOT** open a public GitHub issue for critical security vulnerabilities.

Instead, please report privately using one of these methods:

1. **GitHub Security Advisories** (Preferred):
   - Go to [Security Advisories](https://github.com/CybLow/paginate/security/advisories/new)
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email**:
   - Send details to the maintainer directly
   - Include "SECURITY" in the subject line

### For Non-Critical Issues

For less severe security issues (e.g., minor information disclosure, low-impact vulnerabilities), you may:

1. Open a [Security Issue](https://github.com/CybLow/paginate/issues/new?template=security.md) using our template
2. Use the private reporting methods above if you prefer

### What to Include

When reporting a vulnerability, please include:

1. **Description**: Clear description of the vulnerability
2. **Impact**: What could an attacker achieve?
3. **Steps to Reproduce**: Minimal steps to reproduce the issue
4. **Affected Versions**: Which versions are affected?
5. **Suggested Fix**: If you have ideas on how to fix it (optional)

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt within 48 hours
2. **Initial Assessment**: We will provide an initial assessment within 7 days
3. **Regular Updates**: We will keep you informed of our progress
4. **Fix Timeline**: Critical issues will be prioritized for immediate patching
5. **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Measures

### In Our Codebase

- **Type Safety**: Strict type hints with mypy enforcement
- **Input Validation**: All user inputs are validated
- **Dependency Scanning**: Automated scanning with pip-audit and Dependabot
- **Code Analysis**: Static analysis with Bandit and CodeQL
- **No Secrets**: No hardcoded secrets in the codebase

### In Our CI/CD

- **SBOM Generation**: Software Bill of Materials for supply chain transparency
- **Build Attestation**: SLSA provenance for published packages
- **Signed Releases**: All releases are signed
- **Trusted Publishing**: OIDC-based publishing to PyPI (no API tokens)

## Security Best Practices for Users

When using pypaginate:

1. **Keep Updated**: Always use the latest version
2. **Pin Dependencies**: Use exact version pins in production
3. **Verify Checksums**: Verify package checksums when downloading
4. **Review Dependencies**: Audit transitive dependencies

### Verifying Package Integrity

```bash
# Install with hash verification
pip install pypaginate --require-hashes

# Or verify manually
pip download pypaginate
pip hash pypaginate-*.whl
```

## Known Security Considerations

### SQL Injection Prevention

When using pypaginate with SQLAlchemy:

```python
# SAFE: Using parameterized queries (default behavior)
result = paginate_query(session, query, params)

# UNSAFE: Never interpolate user input into queries
query = text(f"SELECT * FROM users WHERE name = '{user_input}'")  # DON'T DO THIS
```

### Filter Input Validation

When using filter features:

```python
# SAFE: Validated filter input
filter_params = FilterParams.model_validate(user_input)

# UNSAFE: Unvalidated filter expressions
filter_expr = user_input["filter"]  # DON'T DO THIS without validation
```

## Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. **Private Reporting**: Security issues are reported privately
2. **Coordinated Disclosure**: We coordinate with reporters on disclosure timing
3. **Public Advisory**: We publish security advisories after fixes are available
4. **CVE Assignment**: We request CVEs for significant vulnerabilities

## Security Updates

Security updates are announced through:

- [GitHub Security Advisories](https://github.com/CybLow/paginate/security/advisories)
- [GitHub Releases](https://github.com/CybLow/paginate/releases)
- [PyPI Release Notes](https://pypi.org/project/pypaginate/#history)

## Contact

For security-related inquiries:

- **GitHub Security Advisories**: https://github.com/CybLow/paginate/security/advisories/new
- **Maintainer**: [@CybLow](https://github.com/CybLow)

---

Thank you for helping keep pypaginate and its users safe! 🔒
