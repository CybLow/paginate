---
name: sec-owasp
description: >
  Complete OWASP Top 10 (2021) security risks with Python-specific examples
  and mitigations. Covers broken access control, cryptographic failures,
  injection attacks, insecure design, security misconfiguration, vulnerable
  components, authentication failures, data integrity, logging failures, and SSRF.
version: "2.0"
source: owasp
related:
  - sec-basics
  - sec-api
  - sec-ops
  - api-auth
---

## OWASP TOP 10 (2021)

Complete coverage of the OWASP Top 10 security risks with Python-specific mitigations.

---

### A01: Broken Access Control

**Problem:** Users acting outside their intended permissions.

```python
# BAD: No authorization check
@app.get("/users/{user_id}/profile")
async def get_profile(user_id: int):
    return await user_repository.get(user_id)  # Anyone can access any profile!

# BAD: Client-side only checks
@app.delete("/admin/users/{user_id}")
async def delete_user(user_id: int):
    # Relying on frontend to hide button from non-admins
    return await user_repository.delete(user_id)

# GOOD: Server-side authorization
@app.get("/users/{user_id}/profile")
async def get_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
):
    # Users can only access their own profile or admins can access all
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    return await user_repository.get(user_id)


# GOOD: Role-based access control
class Permission(Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    ADMIN = "admin"


def require_permission(permission: Permission):
    """Decorator to enforce permission checks."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            if not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission required: {permission.value}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


@app.delete("/admin/users/{user_id}")
@require_permission(Permission.DELETE_USERS)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    return await user_repository.delete(user_id)
```

**IDOR Prevention (Insecure Direct Object Reference):**
```python
# BAD: Sequential IDs expose data
class Order(Base):
    id = Column(Integer, primary_key=True)  # Predictable: 1, 2, 3...

# GOOD: Use UUIDs
import uuid

class Order(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    
# GOOD: Always verify ownership
async def get_order(order_id: UUID, current_user: User) -> Order:
    order = await order_repository.get(order_id)
    if order is None:
        raise NotFoundError("Order not found")
    if order.user_id != current_user.id:
        # Don't reveal order exists to unauthorized user
        raise NotFoundError("Order not found")
    return order
```

---

### A02: Cryptographic Failures

**Problem:** Exposure of sensitive data due to weak or missing cryptography.

```python
# BAD: Weak algorithms
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # Weak!
password_hash = hashlib.sha1(password.encode()).hexdigest()  # Weak!

# BAD: No salt
password_hash = hashlib.sha256(password.encode()).hexdigest()  # Rainbow table attack!

# GOOD: Use proper password hashing
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,      # Number of parallel threads
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False


# GOOD: Encrypt sensitive data at rest
from cryptography.fernet import Fernet

class EncryptedField:
    """Encrypt sensitive fields before storage."""
    
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.fernet.decrypt(ciphertext.encode()).decode()
```

**Secure random generation:**
```python
import secrets

# BAD: Predictable random
import random
token = ''.join(random.choices('abcdef0123456789', k=32))  # NOT secure!

# GOOD: Cryptographically secure
token = secrets.token_urlsafe(32)  # 256 bits of entropy
token = secrets.token_hex(32)       # 256 bits, hex format
api_key = secrets.token_bytes(32)   # Raw bytes
```

---

### A03: Injection

**Problem:** Untrusted data sent to interpreter as command/query.

```python
# BAD: Command injection
import os

def process_file(filename: str):
    os.system(f"convert {filename} output.pdf")  # Shell injection!

# Attack: filename = "input.jpg; rm -rf /"

# GOOD: Use subprocess with list arguments
import subprocess

def process_file(filename: str):
    # Validate filename first
    if not SAFE_FILENAME_PATTERN.match(filename):
        raise ValidationError("Invalid filename")
    
    # Use list form - no shell interpretation
    subprocess.run(
        ["convert", filename, "output.pdf"],
        check=True,
        capture_output=True,
    )


# BAD: Template injection
from jinja2 import Template

def render_greeting(name: str) -> str:
    template = Template(f"Hello, {name}!")  # SSTI vulnerability!
    return template.render()

# Attack: name = "{{ config.SECRET_KEY }}"

# GOOD: Separate template from data
def render_greeting(name: str) -> str:
    template = Template("Hello, {{ name }}!")
    return template.render(name=name)

# BETTER: Use autoescape
from jinja2 import Environment, select_autoescape

env = Environment(autoescape=select_autoescape(['html', 'xml']))


# BAD: LDAP injection
def find_user(username: str):
    query = f"(uid={username})"  # Injection!
    return ldap.search(query)

# GOOD: Escape special characters
import ldap.filter

def find_user(username: str):
    safe_username = ldap.filter.escape_filter_chars(username)
    query = f"(uid={safe_username})"
    return ldap.search(query)
```

---

### A04: Insecure Design

**Problem:** Missing or ineffective security controls in design.

```python
# BAD: No rate limiting on sensitive operations
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    return await auth_service.login(credentials)  # Brute force vulnerable!

# GOOD: Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login(request: Request, credentials: LoginRequest):
    return await auth_service.login(credentials)


# BAD: No account lockout
async def login(email: str, password: str) -> User:
    user = await get_user_by_email(email)
    if not verify_password(password, user.password_hash):
        raise AuthError("Invalid credentials")
    return user

# GOOD: Account lockout after failures
class LoginService:
    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    
    async def login(self, email: str, password: str) -> User:
        user = await self.get_user_by_email(email)
        
        # Check lockout
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = (user.locked_until - datetime.utcnow()).seconds
            raise AccountLockedError(
                f"Account locked. Try again in {remaining} seconds."
            )
        
        if not verify_password(password, user.password_hash):
            user.failed_attempts += 1
            if user.failed_attempts >= self.MAX_ATTEMPTS:
                user.locked_until = datetime.utcnow() + self.LOCKOUT_DURATION
            await self.user_repository.save(user)
            raise AuthError("Invalid credentials")
        
        # Reset on success
        user.failed_attempts = 0
        user.locked_until = None
        await self.user_repository.save(user)
        return user
```

**Security by design patterns:**
```python
# Fail-safe defaults
class UserPermissions:
    def __init__(self):
        self.permissions: set[str] = set()  # Empty by default
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions  # Deny by default


# Defense in depth
class TransferService:
    async def transfer(
        self,
        from_account: Account,
        to_account: Account,
        amount: Decimal,
        current_user: User,
    ) -> Transfer:
        # Layer 1: Authentication (already done via dependency)
        # Layer 2: Authorization
        if from_account.owner_id != current_user.id:
            raise AuthorizationError("Not account owner")
        
        # Layer 3: Business validation
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        if from_account.balance < amount:
            raise InsufficientFundsError()
        
        # Layer 4: Fraud detection
        if await self.fraud_detector.is_suspicious(from_account, amount):
            await self.notify_security_team(from_account, amount)
            raise TransferBlockedError("Transfer flagged for review")
        
        # Layer 5: Transaction integrity
        async with self.db.transaction():
            from_account.balance -= amount
            to_account.balance += amount
            transfer = Transfer(from_account, to_account, amount)
            await self.repository.save_all([from_account, to_account, transfer])
        
        return transfer
```

---

### A05: Security Misconfiguration

**Problem:** Insecure default configurations, incomplete setups.

```python
# BAD: Debug mode in production
app = FastAPI(debug=True)  # Exposes stack traces!

# BAD: Default credentials
DATABASE_URL = "postgresql://admin:admin@localhost/myapp"

# BAD: Verbose error responses
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()}
    )

# GOOD: Environment-based configuration
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
app = FastAPI(debug=DEBUG and os.getenv("ENVIRONMENT") != "production")


# GOOD: Secure error handling
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    # Log full error server-side
    logger.exception("Unhandled exception", extra={"path": request.url.path})
    
    # Return generic error to client
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# GOOD: Security headers
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(
    middleware=[
        Middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]),
    ]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

### A06: Vulnerable and Outdated Components

**Problem:** Using components with known vulnerabilities.

```bash
# Scan for vulnerabilities
uv run pip-audit                    # Check installed packages
uv run safety check                 # Alternative scanner
uv run pip-audit --fix              # Auto-fix where possible

# Scan code for issues
uv run bandit -r src/               # Security linter
uv run semgrep --config=auto src/   # Pattern-based scanning
```

```yaml
# .github/workflows/security.yml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Dependency audit
      run: |
        uv run pip-audit --strict --desc
        
    - name: Code security scan
      run: |
        uv run bandit -r src/ -ll -ii
        
    - name: SAST with Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/python
          p/security-audit
          p/secrets
```

---

### A07: Identification and Authentication Failures

**Problem:** Weak authentication mechanisms, session management.

```python
# BAD: Weak session ID generation
import random
session_id = str(random.randint(100000, 999999))  # Only 900,000 possibilities!

# GOOD: Secure session ID
import secrets
session_id = secrets.token_urlsafe(32)  # 256 bits of entropy


# BAD: No session expiration
sessions = {}  # Sessions live forever!

# GOOD: Session with expiration
from datetime import datetime, timedelta

@dataclass
class Session:
    id: str
    user_id: int
    created_at: datetime
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class SessionManager:
    SESSION_DURATION = timedelta(hours=24)
    
    def create(self, user_id: int) -> Session:
        now = datetime.utcnow()
        return Session(
            id=secrets.token_urlsafe(32),
            user_id=user_id,
            created_at=now,
            expires_at=now + self.SESSION_DURATION,
        )
    
    def validate(self, session_id: str) -> Session:
        session = self.session_store.get(session_id)
        if session is None:
            raise InvalidSessionError()
        if session.is_expired:
            self.session_store.delete(session_id)
            raise SessionExpiredError()
        return session


# GOOD: Multi-factor authentication
class MFAService:
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret for user."""
        return pyotp.random_base32()
    
    def verify_totp(self, secret: str, code: str) -> bool:
        """Verify TOTP code."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 1 period drift
    
    def generate_backup_codes(self, count: int = 10) -> list[str]:
        """Generate one-time backup codes."""
        return [secrets.token_hex(4).upper() for _ in range(count)]
```

---

### A08: Software and Data Integrity Failures

**Problem:** Code and infrastructure without integrity verification.

```python
# BAD: Unpinned dependencies
# requirements.txt
requests  # Could be any version, including compromised!

# GOOD: Pinned with hashes
# requirements.txt (generated by pip-compile --generate-hashes)
requests==2.31.0 \
    --hash=sha256:58cd2187c01e70e6e26505bca751777aa9f2ee0b7f4300988b709f44e013003f


# GOOD: Verify integrity of downloads
import hashlib

def verify_download(filepath: Path, expected_hash: str) -> bool:
    """Verify file integrity using SHA-256."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash


# GOOD: Sign and verify data
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def sign_data(data: bytes, private_key_pem: bytes) -> bytes:
    """Sign data with RSA private key."""
    private_key = load_pem_private_key(private_key_pem, password=None)
    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return signature
```

---

### A09: Security Logging and Monitoring Failures

**Problem:** Insufficient logging, no alerting on attacks.

```python
import structlog
from datetime import datetime

logger = structlog.get_logger()

# GOOD: Log security events
class SecurityLogger:
    """Centralized security event logging."""
    
    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
    ) -> None:
        logger.info(
            "login_attempt",
            email=email,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def log_authorization_failure(
        self,
        user_id: int,
        resource: str,
        action: str,
        ip_address: str,
    ) -> None:
        logger.warning(
            "authorization_failure",
            user_id=user_id,
            resource=resource,
            action=action,
            ip_address=ip_address,
            timestamp=datetime.utcnow().isoformat(),
        )


# GOOD: Alert on anomalies
class SecurityMonitor:
    FAILED_LOGIN_THRESHOLD = 10
    TIME_WINDOW = timedelta(minutes=5)
    
    async def check_brute_force(self, ip_address: str) -> None:
        """Detect brute force attacks."""
        recent_failures = await self.get_recent_failures(
            ip_address,
            self.TIME_WINDOW,
        )
        
        if len(recent_failures) >= self.FAILED_LOGIN_THRESHOLD:
            await self.alert_service.send(
                AlertLevel.HIGH,
                f"Possible brute force attack from {ip_address}",
                details={"failed_attempts": len(recent_failures)},
            )
            # Automatically block IP
            await self.firewall.block_ip(ip_address, duration=timedelta(hours=1))
```

---

### A10: Server-Side Request Forgery (SSRF)

**Problem:** Server fetches user-supplied URLs without validation.

```python
# BAD: Fetch any URL user provides
import httpx

@app.post("/fetch-url")
async def fetch_url(url: str):
    response = await httpx.get(url)  # SSRF vulnerability!
    return response.text

# Attack: url = "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
# Result: Leaks AWS credentials!

# GOOD: Validate URL against allowlist
from urllib.parse import urlparse
import ipaddress

ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}
BLOCKED_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),      # Private
    ipaddress.ip_network("172.16.0.0/12"),   # Private
    ipaddress.ip_network("192.168.0.0/16"),  # Private
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local (AWS metadata)
    ipaddress.ip_network("127.0.0.0/8"),     # Localhost
]


def validate_url(url: str) -> str:
    """Validate URL is safe to fetch."""
    parsed = urlparse(url)
    
    # Only allow HTTPS
    if parsed.scheme != "https":
        raise ValidationError("Only HTTPS URLs allowed")
    
    # Check against allowlist
    if parsed.hostname not in ALLOWED_HOSTS:
        raise ValidationError(f"Host not allowed: {parsed.hostname}")
    
    return url


def is_safe_ip(ip_str: str) -> bool:
    """Check if IP is not in blocked ranges."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return not any(ip in network for network in BLOCKED_IP_RANGES)
    except ValueError:
        return False


@app.post("/fetch-url")
async def fetch_url(url: str):
    validated_url = validate_url(url)
    
    # Additionally resolve and check IP
    import socket
    hostname = urlparse(validated_url).hostname
    ip = socket.gethostbyname(hostname)
    
    if not is_safe_ip(ip):
        raise ValidationError("URL resolves to blocked IP range")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(validated_url, follow_redirects=False)
    
    return response.text
```

---

## Quick Reference

### OWASP Top 10 Summary

| Risk | Key Mitigation |
|------|----------------|
| A01: Broken Access Control | RBAC, check ownership, use UUIDs |
| A02: Cryptographic Failures | Argon2 for passwords, TLS, encrypt at rest |
| A03: Injection | Parameterized queries, input validation |
| A04: Insecure Design | Threat modeling, rate limiting, lockouts |
| A05: Security Misconfiguration | Secure defaults, security headers |
| A06: Vulnerable Components | pip-audit, Dependabot, regular updates |
| A07: Auth Failures | Secure sessions, MFA, proper password handling |
| A08: Data Integrity | Hash verification, signed packages |
| A09: Logging Failures | Security logs, alerting, audit trails |
| A10: SSRF | URL allowlist, block internal IPs |

---

## Related Skills

- `sec-basics` - Foundational security practices
- `sec-ops` - Security in CI/CD, SAST/DAST, threat modeling
- `sec-api` - API security, JWT, rate limiting
