"""Generate API reference pages automatically from source code docstrings.

This script is executed by mkdocs-gen-files during the build process.
It scans the src/pypaginate directory and creates markdown files for each module.
"""

from pathlib import Path

import mkdocs_gen_files


nav = mkdocs_gen_files.Nav()

# Root path for source code
src_path = Path("src/pypaginate")

# Modules to document (in order)
MODULES = [
    # Core
    ("pypaginate", "Core package exports"),
    ("pypaginate.core", "Core types and data structures"),
    ("pypaginate.core.pages", "Page and PageParams classes"),
    ("pypaginate.core.context", "Pagination context"),
    ("pypaginate.core.snapshots", "Pagination snapshots"),
    # Engines
    ("pypaginate.engines", "Pagination engines"),
    ("pypaginate.engines.memory", "In-memory pagination"),
    ("pypaginate.engines.sql", "SQL/SQLAlchemy pagination"),
    ("pypaginate.engines.keyset", "Cursor-based pagination"),
    # Query
    ("pypaginate.query", "Query execution"),
    ("pypaginate.query.async_api", "Async pagination functions"),
    # Filters
    ("pypaginate.filters", "Filtering system"),
    ("pypaginate.filters.predicates", "Predicate-based filtering"),
    ("pypaginate.filters.predicates.engine", "Filter engine"),
    ("pypaginate.filters.predicates.builder", "Filter builder"),
    ("pypaginate.filters.predicates.operators", "Filter operators"),
    ("pypaginate.filters.sql_adapter", "SQL filter adapter"),
    # Search
    ("pypaginate.filters.search", "Search functionality"),
    ("pypaginate.filters.search.memory_search", "In-memory search"),
    ("pypaginate.filters.search.sql_search", "SQL search"),
    ("pypaginate.filters.search.options", "Search options"),
    ("pypaginate.filters.search.fuzzy", "Fuzzy matching"),
    # Sorting
    ("pypaginate.sorting", "Sorting utilities"),
    ("pypaginate.sorting.engine", "Sort engine"),
    ("pypaginate.sorting.sql_adapter", "SQL sort adapter"),
    # Text
    ("pypaginate.text", "Text processing"),
    ("pypaginate.text.pipelines", "Text pipelines"),
    ("pypaginate.text.patterns", "Text patterns"),
    ("pypaginate.text.utf8", "UTF-8 utilities"),
    # Database
    ("pypaginate.database", "Database utilities"),
    ("pypaginate.database.collations", "Database collations"),
    ("pypaginate.database.types", "Database types"),
    # Integrations
    ("pypaginate.integrations", "Framework integrations"),
    ("pypaginate.integrations.fastapi", "FastAPI integration"),
    # Other
    ("pypaginate.types", "Type definitions"),
    ("pypaginate.exceptions", "Exception classes"),
    ("pypaginate.dependencies", "Dependency injection"),
]

# Generate a page for each module
for module_path, description in MODULES:
    # Convert module path to file path
    parts = module_path.split(".")
    doc_path = Path("api", *parts[1:]) if len(parts) > 1 else Path("api")
    doc_path = doc_path.with_suffix(".md")

    # Handle __init__ modules
    if len(parts) == 1:
        doc_path = Path("api/index.md")
    elif len(parts) == 2:
        doc_path = Path(f"api/{parts[1]}.md")
    else:
        doc_path = Path(f"api/{'/'.join(parts[1:])}.md")

    # Write the documentation file
    with mkdocs_gen_files.open(doc_path, "w") as fd:
        fd.write(f"# {parts[-1]}\n\n")
        fd.write(f"{description}\n\n")
        fd.write(f"::: {module_path}\n")

    # Set edit path to the source file
    source_file = Path("src", *parts).with_suffix(".py")
    if not source_file.exists():
        source_file = Path("src", *parts, "__init__.py")

    mkdocs_gen_files.set_edit_path(doc_path, source_file)
