"""FastAPI integration example.

Turn a request's query string into pypaginate specs with the FastAPI adapter's
``Annotated`` dependencies, then paginate a SQLAlchemy query with the async
backend. Invalid page/limit values are reported as HTTP 422 automatically.

Requirements:
    pip install "pypaginate[fastapi,sqlalchemy]" uvicorn aiosqlite

Run:
    uvicorn examples.fastapi_integration:app --reload
    # then open http://localhost:8000/docs
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pypaginate import FilterSpec, OffsetPage
from pypaginate.adapters.fastapi import OffsetDep, SortDep
from pypaginate.adapters.sqlalchemy import SQLAlchemyBackend, build_filter, build_order_by


# --- Database -----------------------------------------------------------------
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))


engine = create_async_engine("sqlite+aiosqlite:///:memory:")
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


# --- Schemas ------------------------------------------------------------------
class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class UserPage(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    pages: int
    has_next: bool
    has_previous: bool


def to_response(page: OffsetPage[User]) -> UserPage:
    """Map an OffsetPage of ORM rows onto the Pydantic response model."""
    return UserPage(
        items=[UserOut.model_validate(u) for u in page],
        total=page.total,
        page=page.page,
        pages=page.pages,
        has_next=page.has_next,
        has_previous=page.has_previous,
    )


# --- App ----------------------------------------------------------------------
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        session.add_all(User(name=f"User {i}", email=f"user{i}@example.com") for i in range(1, 101))
        await session.commit()
    yield


app = FastAPI(title="pypaginate FastAPI example", lifespan=lifespan)


@app.get("/users")
async def list_users(
    params: OffsetDep,
    sort: SortDep,
    session: Annotated[AsyncSession, Depends(get_session)],
    name: str | None = None,
) -> UserPage:
    """List users with pagination, optional `?name=` filter, and `?sort=`.

    Examples:
        /users?page=1&limit=20
        /users?name=User 1&sort=-name
    """
    stmt = select(User)
    if name:
        where = build_filter(User, [FilterSpec(field="name", operator="contains", value=name)])
        if where is not None:
            stmt = stmt.where(where)
    stmt = stmt.order_by(*build_order_by(User, sort)) if sort else stmt.order_by(User.id)

    page = await SQLAlchemyBackend(session).paginate(stmt, params)
    return to_response(page)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
