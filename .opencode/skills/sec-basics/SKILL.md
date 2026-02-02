---
name: sec-basics
description: >
  Foundational security practices for Python applications. Covers input validation 
  with whitelists, SQL injection prevention with parameterized queries, secrets 
  management, authentication/authorization patterns, secure error messages, and 
  dependency security scanning.
version: "2.0"
source: mixed
related:
  - sec-owasp
  - sec-api
  - sec-ops
  - api-auth
---

## SECURITY BEST PRACTICES

Security is not optional. These practices prevent common vulnerabilities.

---

### Input Validation

**Validate at boundaries:**
```python
# GOOD: Validate in constructor
class UserId:
    def __init__(self, value: int) -> None:
        if value <= 0:
            raise ValueError(f"User ID must be positive, got {value}")
        self._value = value

    @property
    def value(self) -> int:
        return self._value


# GOOD: Validate in API layer
@dataclass
class CreateUserRequest:
    email: str
    password: str
    name: str

    def __post_init__(self) -> None:
        if not self.email or "@" not in self.email:
            raise ValidationError("Valid email required")
        if len(self.password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not self.name.strip():
            raise ValidationError("Name required")
```

**Whitelist over blacklist:**
```python
# BAD: Blacklist (incomplete, can be bypassed)
FORBIDDEN_CHARS = ["<", ">", "&", '"', "'"]

def sanitize(text: str) -> str:
    for char in FORBIDDEN_CHARS:
        text = text.replace(char, "")
    return text

# GOOD: Whitelist (explicit allowed values)
ALLOWED_OPERATORS = frozenset({"eq", "ne", "gt", "lt", "gte", "lte", "in", "contains"})

def validate_operator(operator: str) -> str:
    if operator not in ALLOWED_OPERATORS:
        raise ValidationError(f"Invalid operator: {operator}")
    return operator


# GOOD: Whitelist allowed fields
SORTABLE_FIELDS = frozenset({"name", "created_at", "price", "rating"})

def validate_sort_field(field: str) -> str:
    if field not in SORTABLE_FIELDS:
        raise ValidationError(f"Cannot sort by: {field}")
    return field
```

**Never trust user input:**
```python
# BAD: Using user input directly
def get_file(filename: str) -> bytes:
    path = f"/uploads/{filename}"  # Path traversal vulnerability!
    return Path(path).read_bytes()

# GOOD: Validate and sanitize
def get_file(filename: str) -> bytes:
    # Remove path components
    safe_name = Path(filename).name
    if safe_name != filename:
        raise SecurityError("Invalid filename")

    # Validate against whitelist
    if not ALLOWED_EXTENSIONS.match(safe_name):
        raise SecurityError("File type not allowed")

    path = UPLOAD_DIR / safe_name
    if not path.exists():
        raise NotFoundError(f"File not found: {safe_name}")

    return path.read_bytes()
```

---

### SQL Injection Prevention

**Always use parameterized queries:**
```python
# BAD: String concatenation (SQL injection!)
def find_user(email: str) -> User:
    query = f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!
    return db.execute(query).first()

# Attack: email = "' OR '1'='1"
# Result: SELECT * FROM users WHERE email = '' OR '1'='1'

# GOOD: Parameterized query
def find_user(email: str) -> User:
    query = "SELECT * FROM users WHERE email = :email"
    return db.execute(text(query), {"email": email}).first()


# GOOD: ORM (parameters handled automatically)
def find_user(email: str) -> User:
    return session.query(User).filter(User.email == email).first()


# GOOD: SQLAlchemy Core
def find_user(email: str) -> User:
    stmt = select(User).where(User.email == email)
    return session.execute(stmt).scalar_one_or_none()
```

**Dynamic queries safely:**
```python
# BAD: Dynamic column names (injection risk)
def sort_users(column: str) -> list[User]:
    query = f"SELECT * FROM users ORDER BY {column}"  # VULNERABLE!
    return db.execute(query).all()

# GOOD: Validate against whitelist
ALLOWED_SORT_COLUMNS = {"name", "email", "created_at"}

def sort_users(column: str) -> list[User]:
    if column not in ALLOWED_SORT_COLUMNS:
        raise ValidationError(f"Invalid sort column: {column}")

    stmt = select(User).order_by(getattr(User, column))
    return session.execute(stmt).scalars().all()
```

---

### Secrets Management

**Never hardcode secrets:**
```python
# BAD: Hardcoded secret
API_KEY = "sk_live_abc123xyz"  # NEVER DO THIS!

# BAD: Secret in code, even if "hidden"
API_KEY = base64.b64decode("c2tfbGl2ZV9hYmMxMjN4eXo=").decode()  # Still bad!

# GOOD: Environment variable
import os

API_KEY = os.environ["API_KEY"]  # Fails loudly if not set

# GOOD: With default for optional secrets
DEBUG_KEY = os.environ.get("DEBUG_KEY")  # None if not set
```

**Never commit secrets:**
```gitignore
# .gitignore
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
secrets.yaml
```

**Use secret managers in production:**
```python
# For AWS
import boto3

def get_secret(name: str) -> str:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=name)
    return response["SecretString"]

# For local development
from dotenv import load_dotenv

load_dotenv()  # Loads .env file
```

---

### Authentication & Authorization

**Secure password handling:**
```python
import secrets
import hashlib

# BAD: Plain text or simple hash
def store_password(password: str) -> str:
    return password  # NEVER!
    return hashlib.md5(password.encode()).hexdigest()  # Too weak!
    return hashlib.sha256(password.encode()).hexdigest()  # No salt!

# GOOD: Use proper password hashing
from passlib.hash import argon2

def hash_password(password: str) -> str:
    return argon2.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return argon2.verify(password, hash)
```

**Secure token generation:**
```python
import secrets

# GOOD: Cryptographically secure tokens
def generate_api_key() -> str:
    return secrets.token_urlsafe(32)  # 256 bits of entropy

def generate_reset_token() -> str:
    return secrets.token_hex(32)  # 256 bits of entropy

# GOOD: Time-limited tokens
import jwt
from datetime import datetime, timedelta

def generate_jwt(user_id: int, secret: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

---

### Error Messages

**Don't leak sensitive information:**
```python
# BAD: Reveals system details
def login(email: str, password: str) -> User:
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        raise AuthError("No user found with email: " + email)  # Reveals valid emails!
    if not verify_password(password, user.password_hash):
        raise AuthError(f"Invalid password for user {user.id}")  # Reveals user exists!
    return user

# GOOD: Generic error message
def login(email: str, password: str) -> User:
    user = db.query(User).filter_by(email=email).first()
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("Invalid email or password")  # Same message for both cases
    return user
```

**Log details server-side:**
```python
import logging

logger = logging.getLogger(__name__)

def process_payment(order_id: int, card_token: str) -> PaymentResult:
    try:
        result = payment_gateway.charge(card_token, amount)
        return result
    except PaymentError as e:
        # Log full details for debugging
        logger.error(
            "Payment failed",
            extra={
                "order_id": order_id,
                "error_code": e.code,
                "error_details": str(e),
            },
        )
        # Return generic message to user
        raise PaymentError("Payment could not be processed. Please try again.")
```

---

### Dependency Security

**Pin dependencies:**
```toml
# pyproject.toml - pin major.minor for stability
dependencies = [
    "sqlalchemy>=2.0,<3.0",
    "pydantic>=2.0,<3.0",
]

# For reproducible builds, use lock file
# uv.lock is automatically maintained by uv
```

**Security scanning:**
```bash
# Scan for known vulnerabilities
uv run pip-audit

# Scan code for security issues
uv run bandit -r src/

# In CI/CD - fail on vulnerabilities
uv run pip-audit --strict
uv run bandit -r src/ -ll  # Only high severity
```

**Keep dependencies updated:**
```bash
# Check for outdated packages
uv pip list --outdated

# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package@latest
```

---

## Quick Reference

### Security Checklist

**Before every release:**
- [ ] No secrets in code or config files
- [ ] All user input validated
- [ ] Parameterized queries everywhere
- [ ] Secure password hashing
- [ ] Generic error messages to users
- [ ] Dependencies scanned for vulnerabilities
- [ ] Security headers configured (for web apps)
- [ ] HTTPS enforced (for web apps)
- [ ] Rate limiting in place (for APIs)
- [ ] Logging doesn't include sensitive data

### Security Scanning Commands

```bash
# Dependency vulnerabilities
uv run pip-audit                     # Check installed packages
uv run pip-audit --fix               # Auto-fix where possible

# Code security (SAST)
uv run bandit -r src/                # Security linter
uv run bandit -r src/ -ll -ii        # High severity only
```

---

## Related Skills

- `sec-owasp` - OWASP Top 10 vulnerabilities and mitigations
- `sec-ops` - Security in CI/CD, SAST/DAST, threat modeling
- `sec-api` - API security, JWT, rate limiting, CORS
