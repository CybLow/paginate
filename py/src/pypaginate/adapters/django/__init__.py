"""Django adapter: filter/sort/search to ``Q``/``order_by`` plus pagination.

Django is imported lazily inside the helpers, so importing this module does not
require Django to be installed — only calling a helper does. Install the extra
with ``pip install pypaginate[django]``.
"""

from __future__ import annotations

from pypaginate.adapters.django.backend import paginate_keyset, paginate_offset
from pypaginate.adapters.django.filters import apply_filters, build_filter_q
from pypaginate.adapters.django.search import apply_search, build_search_q
from pypaginate.adapters.django.sorting import apply_sorting, build_order_by


__all__ = [
    "apply_filters",
    "apply_search",
    "apply_sorting",
    "build_filter_q",
    "build_order_by",
    "build_search_q",
    "paginate_keyset",
    "paginate_offset",
]
