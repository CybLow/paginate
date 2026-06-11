# pypaginate examples

Runnable scripts demonstrating pypaginate features. Each is self-contained; run
it with `uv run python examples/<name>.py` from the `py/` directory.

## Examples

### [basic_pagination.py](./basic_pagination.py)
Offset pagination over an in-memory list with `paginate()` and `OffsetParams` —
page metadata, indexing, and out-of-range behaviour.

```bash
uv run python examples/basic_pagination.py
```

### [filtering.py](./filtering.py)
Filtering with `filter()` and `FilterSpec`: equality, comparisons, membership
(`in`), and nested `And()` / `Or()` boolean groups.

```bash
uv run python examples/filtering.py
```

### [keyset_pagination.py](./keyset_pagination.py)
Cursor (keyset) pagination with the SQLAlchemy adapter over in-memory SQLite —
portable, byte-compatible cursors and forward/backward navigation.

```bash
pip install "pypaginate[sqlalchemy]"
uv run python examples/keyset_pagination.py
```

### [fastapi_integration.py](./fastapi_integration.py)
A FastAPI app using the `OffsetDep` / `SortDep` dependencies and the async
SQLAlchemy backend, with an optional `?name=` filter.

```bash
pip install "pypaginate[fastapi,sqlalchemy]" uvicorn aiosqlite
uvicorn examples.fastapi_integration:app --reload
# then open http://localhost:8000/docs
```

## Installing extras

```bash
pip install "pypaginate[sqlalchemy]"   # SQLAlchemy offset + keyset adapter
pip install "pypaginate[fastapi]"      # FastAPI dependencies (+ Pydantic)
pip install "pypaginate[django]"       # Django Q-object builders
pip install "pypaginate[all]"          # everything
```

See the full documentation at <https://cyblow.github.io/paginate/>.
