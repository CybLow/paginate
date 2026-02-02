---
description: Check dependencies for updates and vulnerabilities
agent: build
---

Check project dependencies for updates, vulnerabilities, and issues.

## Commands

### 1. List Outdated Packages
```bash
uv pip list --outdated
```

### 2. Check for Vulnerabilities
```bash
uv run pip-audit
```

### 3. View Dependency Tree
```bash
uv pip tree
```

### 4. Check pyproject.toml
Read `pyproject.toml` to understand:
- Direct dependencies
- Version constraints
- Optional dependencies
- Dev dependencies

## Analysis

### Outdated Dependencies
| Package | Current | Latest | Type | Risk |
|---------|---------|--------|------|------|
| name | 1.0.0 | 2.0.0 | Major | Breaking changes possible |
| name | 1.0.0 | 1.1.0 | Minor | New features, should be safe |
| name | 1.0.0 | 1.0.1 | Patch | Bug fixes, safe to update |

### Security Vulnerabilities
| Package | CVE | Severity | Fix Version |
|---------|-----|----------|-------------|
| name | CVE-XXXX | High | X.Y.Z |

### Recommendations

#### Immediate (Security)
Packages with known vulnerabilities:
```bash
uv add package>=safe_version
```

#### Soon (Major Updates)
Major version updates to review:
- [ ] package: 1.x → 2.x (breaking changes: ...)

#### Routine (Minor/Patch)
Safe updates:
```bash
uv add package1 package2 package3
```

## Update Commands

```bash
# Update specific package
uv add package>=new_version

# Update all (careful with major versions)
uv sync --upgrade

# Lock dependencies
uv lock
```

## Arguments

$ARGUMENTS

Options:
- `--update`: Apply safe updates (minor/patch)
- `--security`: Only show security issues
- `--outdated`: Only show outdated packages
