---
name: api-auth
description: >
  API authentication and rate limiting. Covers API keys, JWT, OAuth2 with scopes,
  rate limiting strategies, and implementation with FastAPI. Essential for securing APIs.
related:
  - api-rest
  - api-gateway
  - sec-basics
  - sec-api
---

## AUTHENTICATION METHODS

Choose the right authentication for your API.

---

### Authentication Comparison

| Method | Use Case | Security | Complexity |
|--------|----------|----------|------------|
| API Key | Server-to-server, simple | Medium | Low |
| JWT | Stateless, scalable | High | Medium |
| OAuth2 | Third-party access | High | High |
| Session | Traditional web apps | High | Medium |

### API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(
    api_key: str = Security(api_key_header),
    api_key_service: APIKeyService = Depends(),
) -> APIKeyData:
    """Verify API key and return associated data."""
    key_data = await api_key_service.validate(api_key)
    if key_data is None:
        raise HTTPException(401, "Invalid API key")
    return key_data


@app.get("/data")
async def get_data(key_data: APIKeyData = Depends(verify_api_key)):
    # key_data contains: user_id, permissions, rate_limit_tier, etc.
    return await data_service.get()
```

### JWT Authentication

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(),
) -> User:
    """Extract and validate JWT, return user."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
            
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
    user = await user_service.get(int(user_id))
    if user is None:
        raise HTTPException(401, "User not found")
    
    return user


# Token generation
def create_access_token(user_id: int, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
```

### OAuth2 with Scopes

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "read:users": "Read user information",
        "write:users": "Create and update users",
        "read:orders": "Read order information",
        "write:orders": "Create and update orders",
        "admin": "Full administrative access",
    },
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> User:
    """Validate token and check scopes."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        token_scopes = payload.get("scopes", [])
        
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
    # Check required scopes
    for scope in security_scopes.scopes:
        if scope not in token_scopes and "admin" not in token_scopes:
            raise HTTPException(
                403,
                f"Permission denied. Required scope: {scope}",
            )
    
    return await user_service.get(payload["sub"])


@app.get("/users")
async def list_users(
    user: User = Security(get_current_user, scopes=["read:users"]),
):
    """Requires read:users scope."""
    return await user_service.list()


@app.post("/users")
async def create_user(
    data: CreateUserRequest,
    user: User = Security(get_current_user, scopes=["write:users"]),
):
    """Requires write:users scope."""
    return await user_service.create(data)
```

---

## RATE LIMITING

Protect your API from abuse.

---

### Rate Limiting Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| Fixed Window | Count requests in fixed time window | Simple, some burst allowed |
| Sliding Window | Rolling time window | Smoother limiting |
| Token Bucket | Tokens refill over time | Allows controlled bursts |
| Leaky Bucket | Constant output rate | Strict rate enforcement |

### Implementation with slowapi

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/search")
@limiter.limit("30/minute")
async def search(request: Request, q: str):
    """Rate limited to 30 requests per minute per IP."""
    return await search_service.search(q)


@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    """Strict rate limit on login attempts."""
    return await auth_service.login()


# Dynamic rate limits based on user tier
def get_rate_limit(request: Request) -> str:
    user = getattr(request.state, "user", None)
    if user is None:
        return "100/hour"  # Anonymous
    
    limits = {
        "free": "1000/hour",
        "pro": "10000/hour",
        "enterprise": "100000/hour",
    }
    return limits.get(user.tier, "1000/hour")


@app.get("/api/data")
@limiter.limit(get_rate_limit)
async def get_data(request: Request):
    return await data_service.get()
```

### Rate Limit Headers

```python
@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add rate limit info to response headers
    if hasattr(request.state, "rate_limit"):
        rl = request.state.rate_limit
        response.headers["X-RateLimit-Limit"] = str(rl.limit)
        response.headers["X-RateLimit-Remaining"] = str(rl.remaining)
        response.headers["X-RateLimit-Reset"] = str(rl.reset_time)
    
    return response
```

---

## BEST PRACTICES

### Token Refresh Pattern

```python
@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    expires_in: int


async def refresh_tokens(refresh_token: str) -> TokenPair:
    """Issue new token pair using refresh token."""
    try:
        payload = jwt.decode(refresh_token, settings.jwt_secret, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid refresh token")
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")
    
    user_id = payload["sub"]
    
    # Invalidate old refresh token (one-time use)
    await token_store.revoke(refresh_token)
    
    # Issue new pair
    return TokenPair(
        access_token=create_access_token(user_id, timedelta(minutes=15)),
        refresh_token=create_refresh_token(user_id, timedelta(days=7)),
        expires_in=900,
    )
```

### Permission Checking

```python
from enum import Enum


class Permission(Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    ADMIN = "admin"


def require_permission(*permissions: Permission):
    """Decorator to require specific permissions."""
    async def dependency(user: User = Depends(get_current_user)) -> User:
        user_permissions = set(user.permissions)
        
        if Permission.ADMIN in user_permissions:
            return user  # Admin has all permissions
        
        required = set(permissions)
        if not required.issubset(user_permissions):
            missing = required - user_permissions
            raise HTTPException(
                403,
                f"Missing permissions: {', '.join(p.value for p in missing)}",
            )
        
        return user
    
    return dependency


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    user: User = Depends(require_permission(Permission.DELETE_USERS)),
):
    return await user_service.delete(user_id)
```

---

## QUICK REFERENCE

### Authentication Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Public API for developers | API Key |
| Single-page application | JWT with refresh |
| Third-party integrations | OAuth2 |
| Mobile application | OAuth2 + PKCE |
| Server-to-server | API Key or mTLS |

### Rate Limit Recommendations

| Endpoint Type | Suggested Limit |
|---------------|-----------------|
| Authentication | 5-10/minute |
| Search | 30-60/minute |
| Read operations | 100-1000/hour |
| Write operations | 60-300/hour |
| Expensive operations | 10-30/hour |
