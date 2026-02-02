---
name: api-grpc
description: >
  gRPC API design for Python. Covers when to use gRPC vs REST, Protocol Buffer definitions,
  service implementation, client usage, streaming patterns, and error handling.
  Ideal for internal microservice communication.
related:
  - api-rest
  - api-graphql
  - arch-microservices
  - perf-core
---

## GRPC

gRPC is ideal for internal service-to-service communication with high performance needs.

---

### When to Use gRPC vs REST

| Use gRPC When | Use REST When |
|---------------|---------------|
| Internal microservices | Public APIs |
| High throughput needed | Browser clients |
| Strong typing required | Human-readable payloads |
| Bi-directional streaming | Simple request-response |
| Language interoperability | Wide tooling support |

### Protocol Buffer Definition

```protobuf
// user.proto
syntax = "proto3";

package user.v1;

// User service definition
service UserService {
  // Unary RPC
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc UpdateUser(UpdateUserRequest) returns (User);
  rpc DeleteUser(DeleteUserRequest) returns (Empty);
  
  // Server streaming
  rpc ListUsers(ListUsersRequest) returns (stream User);
  
  // Bidirectional streaming
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  UserStatus status = 4;
  google.protobuf.Timestamp created_at = 5;
}

enum UserStatus {
  USER_STATUS_UNSPECIFIED = 0;
  USER_STATUS_ACTIVE = 1;
  USER_STATUS_INACTIVE = 2;
}

message GetUserRequest {
  int64 id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
  string password = 3;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;  // e.g., "status=active"
}

message Empty {}
```

### gRPC Server Implementation

```python
# user_service.py
import grpc
from concurrent import futures
from user_pb2 import User, GetUserRequest, CreateUserRequest
from user_pb2_grpc import UserServiceServicer, add_UserServiceServicer_to_server


class UserServiceImpl(UserServiceServicer):
    """gRPC service implementation."""
    
    def __init__(self, repository: UserRepository):
        self._repository = repository
    
    async def GetUser(
        self,
        request: GetUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> User:
        user = await self._repository.get(request.id)
        if user is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"User {request.id} not found")
        return self._to_proto(user)
    
    async def CreateUser(
        self,
        request: CreateUserRequest,
        context: grpc.aio.ServicerContext,
    ) -> User:
        try:
            user = await self._repository.create(
                name=request.name,
                email=request.email,
                password=request.password,
            )
            return self._to_proto(user)
        except DuplicateEmailError:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Email already registered")
    
    async def ListUsers(
        self,
        request: ListUsersRequest,
        context: grpc.aio.ServicerContext,
    ):
        """Server streaming - yield users one by one."""
        async for user in self._repository.stream_all(
            page_size=request.page_size,
            page_token=request.page_token,
        ):
            yield self._to_proto(user)
    
    def _to_proto(self, user: UserEntity) -> User:
        return User(
            id=user.id,
            name=user.name,
            email=user.email,
            status=UserStatus.USER_STATUS_ACTIVE,
        )


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    add_UserServiceServicer_to_server(UserServiceImpl(repository), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()
```

### gRPC Client

```python
# client.py
import grpc
from user_pb2 import GetUserRequest, CreateUserRequest
from user_pb2_grpc import UserServiceStub


class UserClient:
    """gRPC client for user service."""
    
    def __init__(self, host: str = "localhost:50051"):
        self._channel = grpc.aio.insecure_channel(host)
        self._stub = UserServiceStub(self._channel)
    
    async def get_user(self, user_id: int) -> User:
        request = GetUserRequest(id=user_id)
        return await self._stub.GetUser(request)
    
    async def create_user(self, name: str, email: str, password: str) -> User:
        request = CreateUserRequest(name=name, email=email, password=password)
        return await self._stub.CreateUser(request)
    
    async def list_users(self, page_size: int = 100):
        """Stream users from server."""
        request = ListUsersRequest(page_size=page_size)
        async for user in self._stub.ListUsers(request):
            yield user
    
    async def close(self):
        await self._channel.close()
```

---

## STREAMING PATTERNS

### Server Streaming

```python
# Server sends multiple responses
async def ListUsers(self, request, context):
    async for user in self._repository.stream_all():
        yield self._to_proto(user)

# Client receives stream
async for user in client.list_users():
    print(user.name)
```

### Client Streaming

```python
# Client sends multiple requests
async def UploadImages(self, request_iterator, context):
    images = []
    async for request in request_iterator:
        images.append(request.image_data)
    return UploadResult(count=len(images))

# Client sends stream
async def upload():
    async def generate_requests():
        for image in images:
            yield UploadRequest(image_data=image)
    return await stub.UploadImages(generate_requests())
```

### Bidirectional Streaming

```python
# Both sides stream
async def Chat(self, request_iterator, context):
    async for message in request_iterator:
        response = await process_message(message)
        yield response
```

---

## ERROR HANDLING

### gRPC Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| OK | Success | Request succeeded |
| CANCELLED | Cancelled | Client cancelled |
| INVALID_ARGUMENT | Bad request | Invalid parameters |
| NOT_FOUND | Not found | Resource doesn't exist |
| ALREADY_EXISTS | Conflict | Duplicate resource |
| PERMISSION_DENIED | Forbidden | Not authorized |
| UNAUTHENTICATED | Unauthorized | No/invalid credentials |
| RESOURCE_EXHAUSTED | Rate limited | Quota exceeded |
| INTERNAL | Server error | Unexpected failure |

### Error Handling Pattern

```python
async def GetUser(self, request, context):
    try:
        user = await self._repository.get(request.id)
        if user is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"User {request.id} not found"
            )
        return self._to_proto(user)
    except ValidationError as e:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
    except Exception as e:
        logger.exception("Unexpected error")
        context.abort(grpc.StatusCode.INTERNAL, "Internal server error")
```

---

## QUICK REFERENCE

### Protocol Comparison

| Aspect | REST | GraphQL | gRPC |
|--------|------|---------|------|
| Transport | HTTP | HTTP | HTTP/2 |
| Format | JSON | JSON | Protobuf |
| Schema | OpenAPI (optional) | Required | Required |
| Caching | HTTP caching | Complex | Custom |
| Use case | Public APIs | Flexible queries | Internal services |
| Learning curve | Low | Medium | Medium |

### Setup Commands

```bash
# Install grpcio-tools
pip install grpcio grpcio-tools

# Generate Python code from proto
python -m grpc_tools.protoc \
    --python_out=. \
    --grpc_python_out=. \
    --proto_path=. \
    user.proto
```
