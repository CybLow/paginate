"""Django backends for pagination, filtering, sorting, and search.

Django is imported lazily (inside methods), so importing this package does not
require Django to be installed — only calling a backend does. Install the extra
with ``pip install pypaginate[django]``.
"""

from __future__ import annotations

from pypaginate.adapters.django.backend import DjangoBackend
from pypaginate.adapters.django.cursor import DjangoCursorBackend
from pypaginate.adapters.django.filters import DjangoFilterBackend
from pypaginate.adapters.django.search import DjangoSearchBackend
from pypaginate.adapters.django.sorting import DjangoSortBackend


__all__ = [
    "DjangoBackend",
    "DjangoCursorBackend",
    "DjangoFilterBackend",
    "DjangoSearchBackend",
    "DjangoSortBackend",
]
