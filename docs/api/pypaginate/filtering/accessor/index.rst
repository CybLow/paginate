pypaginate.filtering.accessor
=============================

.. py:module:: pypaginate.filtering.accessor

.. autoapi-nested-parse::

   Field accessor for resolving dotted paths on dicts and objects.

   Supports nested access like ``"user.profile.email"`` transparently
   across both dict-like and attribute-based containers.

   ``compile_accessor()`` pre-splits the path ONCE and returns a fast
   callable that can be applied N times without per-item overhead.



Functions
---------

.. autoapisummary::

   pypaginate.filtering.accessor.compile_accessor
   pypaginate.filtering.accessor.compile_dict_accessor


Module Contents
---------------

.. py:function:: compile_accessor(field_path: str) -> collections.abc.Callable[[object], object]

   Compile a field path into a fast accessor function.

   Called ONCE per field path. Returns a callable used N times.

   :param field_path: Dot-separated path (e.g. ``"user.name"``).

   :returns: A callable that resolves the path on any item.


.. py:function:: compile_dict_accessor(field_path: str) -> collections.abc.Callable[[object], object]

   Compile accessor optimized for dict items (skips isinstance).


