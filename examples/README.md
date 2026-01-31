# pypaginate Examples

This directory contains example scripts demonstrating various pypaginate features.

## Examples

### [basic_pagination.py](./basic_pagination.py)
Simple offset-based pagination with in-memory data.

```bash
python examples/basic_pagination.py
```

### [filtering.py](./filtering.py)
JSON Logic filtering with various operators (eq, gt, gte, in, and, or).

```bash
python examples/filtering.py
```

### [fastapi_integration.py](./fastapi_integration.py)
Complete FastAPI application with SQLAlchemy integration.

```bash
# Install dependencies
pip install pypaginate[fastapi,sqlalchemy] uvicorn aiosqlite

# Run the server
uvicorn examples.fastapi_integration:app --reload

# Visit http://localhost:8000/docs for API documentation
```

### [keyset_pagination.py](./keyset_pagination.py)
Cursor-based pagination for efficient navigation of large datasets.

```bash
python examples/keyset_pagination.py
```

## Requirements

Install pypaginate with all optional dependencies:

```bash
pip install pypaginate[all]
```

Or install specific features:

```bash
pip install pypaginate[sqlalchemy]  # SQLAlchemy support
pip install pypaginate[fastapi]     # FastAPI integration
pip install pypaginate[filters]     # JSON Logic filtering
pip install pypaginate[search]      # Text search with fuzzy matching
```
