# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html
"""Sphinx configuration for pypaginate documentation.

This configuration provides:
- Modern RTD theme with Material-like UX
- Full Markdown support via MyST parser
- API autodoc with type hints
- Version switching via sphinx-polyversion
- Cards, tabs, dropdowns via sphinx-design
- Copy buttons on code blocks
"""

from __future__ import annotations

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
version = "0.1"
release = "0.1.0"

# =============================================================================
# GENERAL CONFIGURATION
# =============================================================================

extensions = [
    # -------------------------------------------------------------------------
    # Core Sphinx Extensions
    # -------------------------------------------------------------------------
    "sphinx.ext.autodoc",  # Auto-generate from docstrings
    "sphinx.ext.autosummary",  # Generate summary tables
    "sphinx.ext.intersphinx",  # Link to other projects
    "sphinx.ext.napoleon",  # Google/NumPy docstrings
    "sphinx.ext.viewcode",  # Add [source] links
    "sphinx.ext.autosectionlabel",  # Reference sections by title
    # -------------------------------------------------------------------------
    # Theme
    # -------------------------------------------------------------------------
    "sphinx_rtd_theme",
    # -------------------------------------------------------------------------
    # Modern UX Extensions
    # -------------------------------------------------------------------------
    "sphinx_design",  # Cards, grids, tabs, dropdowns
    "sphinx_copybutton",  # Copy button on code blocks
    "sphinx_autodoc_typehints",  # Type hints in API docs
    "sphinxext.opengraph",  # Social media preview cards
    "notfound.extension",  # Custom 404 page
    # -------------------------------------------------------------------------
    # Markdown Support
    # -------------------------------------------------------------------------
    "myst_parser",  # Full Markdown support
    # -------------------------------------------------------------------------
    # Diagrams
    # -------------------------------------------------------------------------
    "sphinxcontrib.mermaid",  # Mermaid diagrams
]

# =============================================================================
# SOURCE FILE SETTINGS
# =============================================================================

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"
root_doc = "index"  # Sphinx 4.0+ alias
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "includes",
    "_generated",
    "**/.ipynb_checkpoints",
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
# AUTODOC SETTINGS
# =============================================================================

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "",  # Don't show __init__ by default
    "undoc-members": False,
    "exclude-members": "__weakref__, __dict__, __module__, __init__, __repr__, __eq__, __hash__",
    "show-inheritance": True,
    "inherited-members": False,
}
autodoc_typehints = "signature"  # Show in signature only, not in description
autodoc_typehints_format = "short"
autodoc_class_signature = "separated"
autodoc_preserve_defaults = True

# Autosummary
autosummary_generate = True
autosummary_generate_overwrite = True
autosummary_imported_members = False

# =============================================================================
# AUTODOC MOCK IMPORTS (for optional dependencies)
# =============================================================================
# All optional dependencies are now installed in the docs group in pyproject.toml.
# Mocking is disabled to allow proper autodoc introspection.
#
# If building docs without optional deps, uncomment:
# autodoc_mock_imports = [
#     "sqlalchemy",
#     "sqlakeyset",
#     "json_logic",
#     "fastapi",
#     "pydantic",
#     "rapidfuzz",
# ]

autodoc_mock_imports: list[str] = []

# =============================================================================
# AUTODOC TYPEHINTS SETTINGS (sphinx-autodoc-typehints)
# =============================================================================

always_document_param_types = True
typehints_defaults = None  # Don't show defaults (avoids ugly <factory> display)
typehints_use_signature = True  # Show param types in signature
typehints_use_signature_return = True  # Show return type in signature
typehints_document_rtype = False  # Don't add "Return type:" in description (avoids duplication)

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
    "conf_py_path": "/docs-sphinx/",
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
    # Navigation
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": True,  # Only show page titles in nav, not H2/H3 sections
    # Branding
    "logo_only": True,  # Show logo only (hide project name text)
    "style_nav_header_background": "#4A7C9B",  # Ocean Blue header
    # Navigation buttons
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    # Version/Language selectors (for RTD hosting)
    # Note: display_version is handled by sphinx-multiversion template
}

# Static files
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["custom.js"]

# Logo and favicon
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.svg"

# Additional settings
html_show_sourcelink = True
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
    (master_doc, "pypaginate.tex", "pypaginate Documentation", author, "manual"),
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
    "myst.header",  # Duplicate header warnings in MyST
    "autosectionlabel.*",  # Duplicate label warnings
    "ref.python",  # Duplicate Python object description warnings (dataclass attrs)
    "sphinx_autodoc_typehints.forward_reference",  # SQLAlchemy forward ref issues
]


# =============================================================================
# AUTODOC CUSTOMIZATION HOOKS
# =============================================================================


def autodoc_skip_member_handler(
    app,  # noqa: ANN001 - Sphinx app
    what: str,
    name: str,
    obj,  # noqa: ANN001 - Can be any Python object
    skip: bool,
    options,  # noqa: ANN001 - Sphinx options dict
) -> bool | None:
    """Skip private members (attributes/methods starting with underscore).

    This prevents private attributes documented in class Attributes:
    sections from appearing in the rendered documentation while still
    allowing dunder methods if explicitly requested.

    Args:
        app: Sphinx application object.
        what: Type of object (module, class, function, etc.).
        name: Name of the member.
        obj: The actual Python object.
        skip: Whether autodoc would skip this member by default.
        options: Options given to the directive.

    Returns:
        True to skip, False to include, None to use default behavior.
    """
    # Skip members starting with single underscore (but not dunder methods)
    if name.startswith("_") and not name.startswith("__"):
        return True
    return None  # Use default behavior for other cases


def setup(app) -> dict:  # noqa: ANN001 - Sphinx app
    """Sphinx application setup hook.

    Connects custom event handlers for autodoc processing.
    """
    app.connect("autodoc-skip-member", autodoc_skip_member_handler)
    return {
        "version": release,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
