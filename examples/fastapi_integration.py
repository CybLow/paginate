"""FastAPI Integration Example.

This example demonstrates how to integrate pypaginate
with a FastAPI application using SQLAlchemy.

Requirements:
    pip install pypaginate[fastapi,sqlalchemy] uvicorn

Run:
    uvicorn examples.fastapi_integration:app --reload
"""

from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pypaginate import PageParams, PagedResponse, get_pagination_params, paginate_entities


# =============================================================================
# Database Setup
# =============================================================================
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))


# In-memory SQLite for demo
engine = create_async_engine("sqlite+aiosqlite:///:memory:")
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:  # type: ignore[misc]
    async with async_session() as session:
        yield session


# =============================================================================
# Pydantic Schemas
# =============================================================================
class UserOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


# =============================================================================
# FastAPI App
# =============================================================================
app = FastAPI(title="pypaginate FastAPI Example")


@app.on_event("startup")
async def startup() -> None:
    """Create tables and seed data."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Seed 100 users
        for i in range(1, 101):
            session.add(User(name=f"User {i}", email=f"user{i}@example.com"))
        await session.commit()


@app.get("/users", response_model=PagedResponse[UserOut])
async def list_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    params: Annotated[PageParams, Depends(get_pagination_params)],
) -> PagedResponse[UserOut]:
    """List users with pagination.

    Query params:
        - page: Page number (default: 1)
        - limit: Items per page (default: 20, max: 100)
    """
    stmt = select(User).order_by(User.id)
    return await paginate_entities(session, stmt, params)


@app.get("/users/search", response_model=PagedResponse[UserOut])
async def search_users(
    session: Annotated[AsyncSession, Depends(get_session)],
    params: Annotated[PageParams, Depends(get_pagination_params)],
    name: str | None = None,
) -> PagedResponse[UserOut]:
    """Search users by name with pagination."""
    stmt = select(User).order_by(User.id)

    if name:
        stmt = stmt.where(User.name.ilike(f"%{name}%"))

    return await paginate_entities(session, stmt, params)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
