"""Sphinx configuration for pypaginate documentation.

This configuration provides:
- Modern RTD theme with Material-like UX
- Full Markdown support via MyST parser
- API autodoc with type hints via sphinx-autoapi
- Version switching via sphinx-polyversion
- Cards, tabs, dropdowns via sphinx-design
- Copy buttons on code blocks
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime


# Add source path for autodoc
sys.path.insert(0, os.path.abspath("../src"))

# =============================================================================
# POLYVERSION DATA (loaded when building with sphinx-polyversion)
# =============================================================================

# Try to load version data from sphinx-polyversion
# This only works when POLYVERSION_DATA env var is set (by sphinx-polyversion driver)
if os.environ.get("POLYVERSION_DATA"):
    try:
        from sphinx_polyversion.api import load

        load(globals())
        # This adds to global scope:
        # html_context["current"] = GitRef(...)
        # html_context["tags"] = [GitRef(...), ...]
        # html_context["branches"] = [GitRef(...), ...]
        # html_context["revisions"] = [GitRef(...), ...]
        # html_context["latest"] = GitRef(...)
    except ImportError:
        # sphinx-polyversion not installed
        pass

# =============================================================================
# PROJECT INFORMATION
# =============================================================================

project = "pypaginate"
copyright = f"2024-{datetime.now().year} CybLow"
author = "CybLow"
version = "0.2"
release = "0.2.0"

# =============================================================================
# GENERAL CONFIGURATION
# =============================================================================

extensions = [
    # Core Sphinx Extensions
    "sphinx.ext.autodoc",  # Auto-generate from docstrings (needed by autoapi)
    "sphinx.ext.intersphinx",  # Link to other projects
    "sphinx.ext.napoleon",  # Google/NumPy docstrings
    "sphinx.ext.autosectionlabel",  # Reference sections by title
    # Theme
    "sphinx_rtd_theme",
    # Modern UX Extensions
    "sphinx_design",  # Cards, grids, tabs, dropdowns
    "sphinx_copybutton",  # Copy button on code blocks
    "sphinx_autodoc_typehints",  # Type hints in API docs
    "sphinxext.opengraph",  # Social media preview cards
    "notfound.extension",  # Custom 404 page
    # API Documentation (auto-generated)
    "autoapi.extension",  # Auto-generate API reference from source
    # Markdown Support
    "myst_parser",  # Full Markdown support
    # Diagrams
    "sphinxcontrib.mermaid",  # Mermaid diagrams
]

# =============================================================================
# SOURCE FILE SETTINGS
# =============================================================================

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
root_doc = "index"
exclude_patterns = [
    "_build",
    "site",
    "Thumbs.db",
    ".DS_Store",
    "includes",
    "_generated",
    "**/.ipynb_checkpoints",
    # Internal planning/architecture docs not part of user-facing toctree
    "ARCHITECTURE.md",
    "FEATURE_GAP_ANALYSIS.md",
    "OPTIMIZATION_AUDIT.md",
    "TESTING.md",
    "contributing/refactoring-plan-v0.1.1.md",
]

# =============================================================================
# MYST PARSER (Markdown) SETTINGS
# =============================================================================

myst_enable_extensions = [
    "colon_fence",  # ::: directive syntax for sphinx-design
    "deflist",  # Definition lists
    "fieldlist",  # Field lists
    "substitution",  # Variable substitution
    "tasklist",  # Checkbox task lists
    "attrs_inline",  # Inline attributes {#id .class}
    "attrs_block",  # Block attributes
]
myst_heading_anchors = 4  # Generate anchors for h1-h4
myst_enable_checkboxes = True

# =============================================================================
# SPHINX-AUTOAPI SETTINGS (Auto-generated API Reference)
# =============================================================================

# Directories containing source code to document
autoapi_dirs = ["../src/pypaginate"]

# Output directory for generated API docs (relative to docs/)
autoapi_root = "api"

# Type of documentation to generate
autoapi_type = "python"

# Template directory for customizing output
autoapi_template_dir = "_templates/autoapi"

# Options for what to include
autoapi_options = [
    "members",  # Document members
    "undoc-members",  # Include undocumented members (we filter via skip)
    "show-inheritance",  # Show class inheritance
    "show-module-summary",  # Add summary at top of module pages
    "imported-members",  # Show members imported into __init__.py
]

# Generate separate pages for each module
autoapi_keep_files = True

# Don't include private members (single underscore)
autoapi_python_use_implicit_namespaces = False

# Member ordering (alphabetical or by source order)
autoapi_member_order = "groupwise"  # Group by type (classes, functions, etc.)

# Add autoapi to toctree automatically
autoapi_add_toctree_entry = False  # We manage toctree manually in index.md

# Ignore test files and internal modules
autoapi_ignore = [
    "**/tests/*",
    "**/_cli.py",
    "**/conftest.py",
]


def autoapi_skip_member(
    app,
    what: str,
    name: str,
    obj,
    skip: bool,
    options,
) -> bool | None:
    """Skip private members, undocumented attributes, and specific patterns.

    Args:
        app: Sphinx application object.
        what: Type of object (module, class, function, etc.).
        name: Full dotted name of the member.
        obj: The actual Python object.
        skip: Whether autoapi would skip this member by default.
        options: Options given to the directive.

    Returns:
        True to skip, False to include, None to use default behavior.
    """
    # Skip private members (single underscore, not dunder)
    short_name = name.split(".")[-1]
    if short_name.startswith("_") and not short_name.startswith("__"):
        return True

    # Skip dunder methods except specific ones we want to document
    if short_name.startswith("__") and short_name.endswith("__"):
        allowed_dunders = {
            "__init__",
            "__call__",
            "__enter__",
            "__exit__",
            "__aenter__",
            "__aexit__",
        }
        if short_name not in allowed_dunders:
            return True

    # Skip undocumented instance attributes (they clutter the API docs)
    # These are typically set in __init__ without docstrings
    if what == "attribute":
        # Check if the attribute has a docstring
        docstring = getattr(obj, "docstring", None) or ""
        if not docstring.strip():
            return True

    return None  # Use default behavior


# =============================================================================
# SPHINX-AUTODOC-TYPEHINTS SETTINGS
# =============================================================================

always_document_param_types = True
typehints_defaults = None  # Don't show defaults (avoids ugly <factory> display)
typehints_use_signature = True  # Show param types in signature
typehints_use_signature_return = True  # Show return type in signature
typehints_document_rtype = False  # Don't add "Return type:" (avoids duplication)

# =============================================================================
# NAPOLEON SETTINGS (Google Docstrings)
# =============================================================================

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# =============================================================================
# INTERSPHINX SETTINGS
# =============================================================================

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
}

# =============================================================================
# AUTOSECTION LABEL SETTINGS
# =============================================================================

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2

# =============================================================================
# COPYBUTTON SETTINGS
# =============================================================================

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.{3,}: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True
copybutton_line_continuation_character = "\\"

# =============================================================================
# MERMAID SETTINGS
# =============================================================================

mermaid_version = "10.6.0"
mermaid_init_js = """
mermaid.initialize({
    startOnLoad: true,
    theme: 'neutral',
    securityLevel: 'loose',
});
"""

# =============================================================================
# GITHUB PAGES SETTINGS
# =============================================================================

# Base URL for canonical links (GitHub Pages)
html_baseurl = "https://cyblow.github.io/pypaginate/"

# Context for "Edit on GitHub" links
html_context = {
    "display_github": True,
    "github_user": "CybLow",
    "github_repo": "pypaginate",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# =============================================================================
# OPENGRAPH SETTINGS (Social Preview)
# =============================================================================

# Using GitHub Pages URL (will change to RTD when public)
ogp_site_url = "https://cyblow.github.io/pypaginate/"
ogp_site_name = "pypaginate Documentation"
ogp_image = "_static/logo.svg"
ogp_description_length = 200
ogp_type = "website"

# =============================================================================
# 404 PAGE SETTINGS
# =============================================================================

# GitHub Pages path prefix
notfound_urls_prefix = "/pypaginate/"

# =============================================================================
# HTML OUTPUT SETTINGS
# =============================================================================

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": True,
    "sticky_navigation": True,
    "prev_next_buttons_location": "bottom",
}

# Static files
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["custom.js"]

# Logo and favicon
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.svg"

# Additional settings
html_show_sourcelink = False  # No [source] links (cleaner look)
html_show_sphinx = False
html_show_copyright = True
html_last_updated_fmt = "%b %d, %Y"

# Template paths (for version selector)
templates_path = ["_templates"]

# =============================================================================
# LATEX OUTPUT SETTINGS (for PDF)
# =============================================================================

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "preamble": r"""
\usepackage{enumitem}
\setlistdepth{99}
""",
}

latex_documents = [
    (root_doc, "pypaginate.tex", "pypaginate Documentation", author, "manual"),
]

# =============================================================================
# EPUB OUTPUT SETTINGS
# =============================================================================

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# =============================================================================
# SUPPRESS WARNINGS
# =============================================================================

suppress_warnings = [
    # "myst.header",  # Re-enabled to fix header structure issues
    "autosectionlabel.*",  # Duplicate label warnings
    "ref.python",  # Duplicate Python object description warnings (dataclass attrs)
    "sphinx_autodoc_typehints.forward_reference",  # SQLAlchemy forward ref issues
    "autoapi.python_import_resolution",  # Optional import warnings
    # Duplicate object description from autoapi v3.2+ (class attributes documented twice)
    # See: https://github.com/readthedocs/sphinx-autoapi/issues/476
    "autoapi",
]

# Ignore duplicate object description warnings for dataclass attributes
# This is a known issue with autoapi and dataclasses - attributes are documented
# both from docstrings and from the class definition
nitpicky = False


# =============================================================================
# SPHINX SETUP HOOKS
# =============================================================================


class _SuppressAutoApiPlaceholder(logging.Filter):
    """Suppress AutoAPI 'Unknown type: placeholder' warnings.

    AutoAPI emits this warning (without a type tag) when it encounters
    TYPE_CHECKING imports that resolve to external packages not indexed
    by AutoAPI.  The warning cannot be silenced via suppress_warnings
    because the AutoAPI mapper intentionally omits the ``type=`` kwarg.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return "Unknown type: placeholder" not in record.getMessage()


def setup(app) -> dict:
    """Sphinx application setup hook."""
    import logging as _logging

    _logging.getLogger("autoapi._mapper").addFilter(_SuppressAutoApiPlaceholder())
    app.connect("autoapi-skip-member", autoapi_skip_member)
    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
