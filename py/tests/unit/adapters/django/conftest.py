"""Configure a minimal Django (in-memory sqlite) for the adapter tests.

No project/app is needed: the throwaway test model declares an explicit
``app_label``, and its table is created directly via the schema editor — so the
Django ORM compiles real SQL and runs real queries without migrations.
"""

from __future__ import annotations

import pytest


pytest.importorskip("django")

from django.conf import settings


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[],
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        },
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        USE_TZ=False,
    )
    import django

    django.setup()
