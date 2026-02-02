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
# NOTE: Top-level modules with manual documentation in docs/api/*.md are EXCLUDED
# to prevent overwriting the manually-written documentation:
#   - pypaginate (root) -> manual docs/api/index.md
#   - pypaginate.core -> manual docs/api/core.md
#   - pypaginate.engines -> manual docs/api/engines.md
#   - pypaginate.filters -> manual docs/api/filters.md
#   - pypaginate.sorting -> manual docs/api/sorting.md
#   - pypaginate.integrations -> manual docs/api/integrations.md
#   - pypaginate.exceptions -> manual docs/api/exceptions.md
#   - pypaginate.filters.search.* -> manual docs/api/search.md
#
# Submodules of manually-documented modules are also EXCLUDED to avoid
# duplicate anchor warnings from mkdocs_autorefs.
MODULES = [
    # Query submodules (no manual docs)
    ("pypaginate.query", "Query execution"),
    ("pypaginate.query.async_api", "Async pagination functions"),
    # Text submodules (no manual docs)
    ("pypaginate.text", "Text processing"),
    ("pypaginate.text.pipelines", "Text pipelines"),
    ("pypaginate.text.patterns", "Text patterns"),
    ("pypaginate.text.utf8", "UTF-8 utilities"),
    # Database submodules (no manual docs)
    ("pypaginate.database", "Database utilities"),
    ("pypaginate.database.collations", "Database collations"),
    ("pypaginate.database.types", "Database types"),
    # Other (no manual docs)
    ("pypaginate.types", "Type definitions"),
    ("pypaginate.dependencies", "Dependency injection"),
]

# Generate a page for each module
for module_path, description in MODULES:
    # Convert module path to file path
    parts = module_path.split(".")
    doc_path = Path("api", *parts[1:]) if len(parts) > 1 else Path("api")
    doc_path = doc_path.with_suffix(".md")

    # Handle module paths
    if len(parts) == 2:
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
