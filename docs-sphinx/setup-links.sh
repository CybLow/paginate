#!/usr/bin/env bash
# Setup script to link markdown files from docs/ to docs-sphinx/
# This allows sharing content between MkDocs and Sphinx

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$(dirname "$SCRIPT_DIR")/docs"
SPHINX_DIR="$SCRIPT_DIR"

echo "Linking documentation files from $DOCS_DIR to $SPHINX_DIR"

# Create directory structure and link files
link_dir() {
    local src_dir="$1"
    local dest_dir="$2"
    
    if [[ -d "$src_dir" ]]; then
        mkdir -p "$dest_dir"
        for file in "$src_dir"/*.md; do
            if [[ -f "$file" ]]; then
                filename=$(basename "$file")
                ln -sf "$file" "$dest_dir/$filename"
                echo "  Linked: $dest_dir/$filename"
            fi
        done
    fi
}

# Link top-level docs directories
link_dir "$DOCS_DIR/getting-started" "$SPHINX_DIR/getting-started"
link_dir "$DOCS_DIR/concepts" "$SPHINX_DIR/concepts"
link_dir "$DOCS_DIR/api" "$SPHINX_DIR/api"
link_dir "$DOCS_DIR/examples" "$SPHINX_DIR/examples"
link_dir "$DOCS_DIR/contributing" "$SPHINX_DIR/contributing"

# Link user-guide subdirectories
link_dir "$DOCS_DIR/user-guide/pagination" "$SPHINX_DIR/pagination"
link_dir "$DOCS_DIR/user-guide/filtering" "$SPHINX_DIR/filtering"
link_dir "$DOCS_DIR/user-guide/search" "$SPHINX_DIR/search"
link_dir "$DOCS_DIR/user-guide/sorting" "$SPHINX_DIR/sorting"
link_dir "$DOCS_DIR/user-guide/integrations" "$SPHINX_DIR/integrations"

# Link root-level files
for file in changelog.md comparison.md CODE_OF_CONDUCT.md; do
    if [[ -f "$DOCS_DIR/$file" ]]; then
        ln -sf "$DOCS_DIR/$file" "$SPHINX_DIR/$file"
        echo "  Linked: $file"
    fi
done

echo ""
echo "Done! To build documentation:"
echo "  1. Install deps: pip install -r requirements.txt"
echo "  2. Build: sphinx-build -b html . _build/html"
