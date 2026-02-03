# Getting Started

Welcome to pypaginate! This section will help you get up and running quickly.

## What is pypaginate?

pypaginate is a modern, framework-agnostic pagination library for Python that provides:

- **Multiple pagination strategies** - Offset-based, cursor-based (keyset), and in-memory
- **Advanced filtering** - JSON Logic with 20+ operators
- **Powerful text search** - Full-text search with fuzzy matching
- **Flexible sorting** - Multi-column with custom sort keys
- **Framework integration** - Native FastAPI and SQLAlchemy support

## Quick Navigation

<div class="grid cards" markdown>

-   :material-download: **[Installation](installation.md)**

    Install pypaginate and optional dependencies

-   :material-rocket-launch: **[Quick Start](quickstart.md)**

    Get paginating in 5 minutes

-   :material-shoe-print: **[First Steps](first-steps.md)**

    Build your first paginated API

</div>

## Minimum Requirements

- **Python 3.11+**
- No runtime dependencies for core functionality

## Optional Dependencies

| Feature | Installation | Provides |
|---------|-------------|----------|
| SQLAlchemy | `pypaginate[sqlalchemy]` | Database pagination |
| Search | `pypaginate[search]` | Fuzzy text search |
| Filters | `pypaginate[filters]` | JSON Logic filtering |
| Text | `pypaginate[text]` | Text normalization |
| FastAPI | `pypaginate[fastapi]` | FastAPI integration |
| All | `pypaginate[all]` | Everything above |

## Next Steps

1. **[Install pypaginate](installation.md)** with your preferred features
2. **[Follow the Quick Start](quickstart.md)** for basic usage
3. **[Build your first API](first-steps.md)** with a complete example
