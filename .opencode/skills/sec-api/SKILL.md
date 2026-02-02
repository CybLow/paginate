---
name: sec-api
description: >
  API security best practices. Covers security headers (CSP, HSTS, X-Frame-Options),
  CORS configuration, rate limiting with Redis, JWT authentication, API key
  management, and container security with Dockerfile best practices.
version: "2.0"
source: mixed
related:
  - sec-basics
  - sec-owasp
  - api-auth
  - api-gateway
---

## SECURITY HEADERS

HTTP headers that protect against common attacks.

---

### Header Configuration

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Force HTTPS
        response.headers["Strict-Transport-Security"] = \
            "max-age=31536000; includeSubDomains; preload"
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Restrict browser features
        response.headers["Permissions-Policy"] = \
            "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.example.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.gstatic.com; "
            "connect-src 'self' https://api.example.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        return response


# Register middleware
app.add_middleware(SecurityHeadersMiddleware)
```

### Header Reference

| Header | Purpose | Recommended Value |
|--------|---------|-------------------|
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` |
| `X-Frame-Options` | Prevent clickjacking | `DENY` or `SAMEORIGIN` |
| `X-XSS-Protection` | XSS filter (legacy) | `1; mode=block` |
| `Strict-Transport-Security` | Force HTTPS | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | Control resource loading | See above |
| `Referrer-Policy` | Control referrer header | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Control browser features | Disable unused features |

---

## CORS CONFIGURATION

Cross-Origin Resource Sharing security.

---

### Secure CORS Setup

```python
from fastapi.middleware.cors import CORSMiddleware

# BAD: Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Never in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GOOD: Explicit origin allowlist
ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://admin.example.com",
]

if os.getenv("ENVIRONMENT") == "development":
    ALLOWED_ORIGINS.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID"],
    max_age=3600,  # Cache preflight for 1 hour
)


# GOOD: Dynamic origin validation
def is_allowed_origin(origin: str) -> bool:
    """Check if origin is allowed."""
    allowed_patterns = [
        r"https://.*\.example\.com$",
        r"https://example\.com$",
    ]
    return any(re.match(pattern, origin) for pattern in allowed_patterns)


class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get("origin")
        
        # Handle preflight
        if request.method == "OPTIONS" and origin:
            if is_allowed_origin(origin):
                return Response(
                    status_code=204,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
                        "Access-Control-Allow-Headers": "Authorization, Content-Type",
                        "Access-Control-Max-Age": "3600",
                    },
                )
            return Response(status_code=403)
        
        response = await call_next(request)
        
        if origin and is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
        
        return response
```

---

## RATE LIMITING

Protect against abuse and denial of service.

---

### Rate Limiting Implementation

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Basic rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/api/items")
@limiter.limit("100/minute")  # 100 requests per minute per IP
async def list_items(request: Request):
    return await item_service.list()


@app.post("/auth/login")
@limiter.limit("5/minute")  # Strict limit on login
async def login(request: Request, credentials: LoginRequest):
    return await auth_service.login(credentials)


# Advanced: Different limits for authenticated users
def get_rate_limit_key(request: Request) -> str:
    """Rate limit by user ID if authenticated, otherwise by IP."""
    if hasattr(request.state, "user"):
        return f"user:{request.state.user.id}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=get_rate_limit_key)


# Dynamic rate limits based on user tier
def get_dynamic_limit(request: Request) -> str:
    """Return rate limit based on user subscription."""
    if hasattr(request.state, "user"):
        tier = request.state.user.subscription_tier
        limits = {
            "free": "100/hour",
            "basic": "1000/hour",
            "premium": "10000/hour",
            "enterprise": "100000/hour",
        }
        return limits.get(tier, "100/hour")
    return "50/hour"  # Unauthenticated


@app.get("/api/data")
@limiter.limit(get_dynamic_limit)
async def get_data(request: Request):
    return await data_service.get()
```

### Redis-backed Rate Limiting

```python
from redis import Redis
from datetime import timedelta


class RateLimiter:
    """Token bucket rate limiter with Redis backend."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window: timedelta,
    ) -> tuple[bool, int]:
        """
        Check if request is allowed.
        
        Returns:
            (allowed, remaining_requests)
        """
        pipe = self.redis.pipeline()
        now = time.time()
        window_start = now - window.total_seconds()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current entries
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiry
        pipe.expire(key, int(window.total_seconds()))
        
        results = pipe.execute()
        current_count = results[1]
        
        if current_count >= max_requests:
            return False, 0
        
        return True, max_requests - current_count - 1


# Usage in middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis: Redis):
        super().__init__(app)
        self.limiter = RateLimiter(redis)
        
    async def dispatch(self, request: Request, call_next) -> Response:
        key = f"ratelimit:{get_remote_address(request)}"
        
        allowed, remaining = await self.limiter.is_allowed(
            key,
            max_requests=100,
            window=timedelta(minutes=1),
        )
        
        if not allowed:
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                headers={
                    "X-RateLimit-Limit": "100",
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                },
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = "100"
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
```

---

## API SECURITY

Secure authentication and authorization for APIs.

---

### JWT Best Practices

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel


class TokenConfig:
    SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class TokenPayload(BaseModel):
    sub: str  # Subject (user ID)
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"
    jti: str  # Unique token ID for revocation


class JWTService:
    def __init__(self, config: TokenConfig):
        self.config = config
        self.revoked_tokens: set[str] = set()  # Use Redis in production
    
    def create_access_token(self, user_id: int) -> str:
        """Create short-lived access token."""
        now = datetime.utcnow()
        payload = TokenPayload(
            sub=str(user_id),
            exp=now + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
            iat=now,
            type="access",
            jti=secrets.token_urlsafe(16),
        )
        return jwt.encode(
            payload.model_dump(),
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM,
        )
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create long-lived refresh token."""
        now = datetime.utcnow()
        payload = TokenPayload(
            sub=str(user_id),
            exp=now + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS),
            iat=now,
            type="refresh",
            jti=secrets.token_urlsafe(16),
        )
        return jwt.encode(
            payload.model_dump(),
            self.config.SECRET_KEY,
            algorithm=self.config.ALGORITHM,
        )
    
    def verify_token(self, token: str, expected_type: str) -> TokenPayload:
        """Verify and decode token."""
        try:
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
            )
            token_data = TokenPayload(**payload)
            
            if token_data.type != expected_type:
                raise InvalidTokenError(f"Expected {expected_type} token")
            
            if token_data.jti in self.revoked_tokens:
                raise RevokedTokenError("Token has been revoked")
            
            return token_data
            
        except JWTError as e:
            raise InvalidTokenError(str(e))
    
    def revoke_token(self, jti: str) -> None:
        """Revoke a token by its ID."""
        self.revoked_tokens.add(jti)


# FastAPI dependency
async def get_current_user(
    authorization: str = Header(...),
    jwt_service: JWTService = Depends(get_jwt_service),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Extract and validate user from JWT."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization[7:]
    token_data = jwt_service.verify_token(token, "access")
    
    user = await user_repository.get(int(token_data.sub))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
```

---

### API Key Authentication

```python
import hashlib
import secrets
from datetime import datetime


class APIKeyService:
    """Secure API key management."""
    
    def generate_key(self, user_id: int, name: str) -> tuple[str, APIKey]:
        """
        Generate new API key.
        
        Returns:
            (raw_key, api_key_record)
            
        Note: raw_key is only shown once!
        """
        # Generate key with prefix for identification
        raw_key = f"sk_live_{secrets.token_urlsafe(32)}"
        
        # Store only the hash
        key_hash = self._hash_key(raw_key)
        
        api_key = APIKey(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            prefix=raw_key[:12],  # Store prefix for identification
            created_at=datetime.utcnow(),
            last_used_at=None,
        )
        
        return raw_key, api_key
    
    def _hash_key(self, raw_key: str) -> str:
        """Hash API key for storage."""
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    async def validate_key(self, raw_key: str) -> APIKey | None:
        """Validate API key and return associated record."""
        key_hash = self._hash_key(raw_key)
        api_key = await self.repository.find_by_hash(key_hash)
        
        if api_key is None:
            return None
        
        if api_key.revoked_at is not None:
            return None
        
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        api_key.last_used_at = datetime.utcnow()
        await self.repository.save(api_key)
        
        return api_key


# FastAPI dependency
async def get_api_key_user(
    x_api_key: str = Header(..., alias="X-API-Key"),
    api_key_service: APIKeyService = Depends(get_api_key_service),
) -> User:
    """Authenticate via API key."""
    api_key = await api_key_service.validate_key(x_api_key)
    if api_key is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API key",
        )
    
    return await user_repository.get(api_key.user_id)
```

---

## CONTAINER SECURITY

Secure Docker deployments.

---

### Dockerfile Best Practices

```dockerfile
# GOOD: Multi-stage build
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim AS production

# Run as non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

# Copy only necessary files
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

# Set ownership
RUN chown -R appuser:appuser /app
USER appuser

# Use specific versions, not latest
ENV PATH="/app/.venv/bin:$PATH"

# Don't run as root
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Container Scanning

```yaml
# .github/workflows/container-security.yml
container-security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Build image
      run: docker build -t myapp:${{ github.sha }} .
      
    - name: Trivy scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: myapp:${{ github.sha }}
        format: 'table'
        exit-code: '1'
        severity: 'CRITICAL,HIGH'
        
    - name: Dockle lint
      uses: goodwithtech/dockle-action@main
      with:
        image: myapp:${{ github.sha }}
        format: 'list'
        exit-code: '1'
        exit-level: 'warn'
```

---

## Quick Reference

### Security Headers (Minimal)

```python
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
}
```

### Rate Limiting Recommendations

| Endpoint Type | Recommended Limit |
|---------------|-------------------|
| Login | 5/minute per IP |
| Password reset | 3/hour per email |
| API (free tier) | 100/hour per user |
| API (paid tier) | 1000+/hour per user |
| Signup | 3/hour per IP |
| General API | 100/minute per IP |

### JWT Checklist

- [ ] Short expiry for access tokens (15 min)
- [ ] Longer expiry for refresh tokens (7 days)
- [ ] Include `jti` for revocation
- [ ] Store refresh tokens securely
- [ ] Rotate refresh tokens on use
- [ ] Use strong secret key (256+ bits)

---

## Related Skills

- `sec-basics` - Foundational security practices
- `sec-owasp` - OWASP Top 10 vulnerabilities
- `sec-ops` - Security in CI/CD, SAST/DAST
