"""Generate API reference pages automatically from source code docstrings.

This script is executed by mkdocs-gen-files during the build process.
It scans the src/pypaginator directory and creates markdown files for each module.
"""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

# Root path for source code
src_path = Path("src/pypaginator")

# Modules to document (in order)
MODULES = [
    # Core
    ("pypaginator", "Core package exports"),
    ("pypaginator.core", "Core types and data structures"),
    ("pypaginator.core.pages", "Page and PageParams classes"),
    ("pypaginator.core.context", "Pagination context"),
    ("pypaginator.core.snapshots", "Pagination snapshots"),
    # Engines
    ("pypaginator.engines", "Pagination engines"),
    ("pypaginator.engines.memory", "In-memory pagination"),
    ("pypaginator.engines.sql", "SQL/SQLAlchemy pagination"),
    ("pypaginator.engines.keyset", "Cursor-based pagination"),
    # Query
    ("pypaginator.query", "Query execution"),
    ("pypaginator.query.async_api", "Async pagination functions"),
    # Filters
    ("pypaginator.filters", "Filtering system"),
    ("pypaginator.filters.predicates", "Predicate-based filtering"),
    ("pypaginator.filters.predicates.engine", "Filter engine"),
    ("pypaginator.filters.predicates.builder", "Filter builder"),
    ("pypaginator.filters.predicates.operators", "Filter operators"),
    ("pypaginator.filters.sql_adapter", "SQL filter adapter"),
    # Search
    ("pypaginator.filters.search", "Search functionality"),
    ("pypaginator.filters.search.memory_search", "In-memory search"),
    ("pypaginator.filters.search.sql_search", "SQL search"),
    ("pypaginator.filters.search.options", "Search options"),
    ("pypaginator.filters.search.fuzzy", "Fuzzy matching"),
    # Sorting
    ("pypaginator.sorting", "Sorting utilities"),
    ("pypaginator.sorting.engine", "Sort engine"),
    ("pypaginator.sorting.sql_adapter", "SQL sort adapter"),
    # Text
    ("pypaginator.text", "Text processing"),
    ("pypaginator.text.pipelines", "Text pipelines"),
    ("pypaginator.text.patterns", "Text patterns"),
    ("pypaginator.text.utf8", "UTF-8 utilities"),
    # Database
    ("pypaginator.database", "Database utilities"),
    ("pypaginator.database.collations", "Database collations"),
    ("pypaginator.database.types", "Database types"),
    # Integrations
    ("pypaginator.integrations", "Framework integrations"),
    ("pypaginator.integrations.fastapi", "FastAPI integration"),
    # Other
    ("pypaginator.types", "Type definitions"),
    ("pypaginator.exceptions", "Exception classes"),
    ("pypaginator.dependencies", "Dependency injection"),
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
