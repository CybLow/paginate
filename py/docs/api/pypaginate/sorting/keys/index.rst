pypaginate.sorting.keys
=======================

.. py:module:: pypaginate.sorting.keys

.. autoapi-nested-parse::

   Sort key building utilities.

   Constructs callable sort keys that handle null placement and
   direction for use with Python's built-in ``sorted()``.

   Uses compiled field accessors to avoid per-item string splitting.



Functions
---------

.. autoapisummary::

   pypaginate.sorting.keys.build_sort_key


Module Contents
---------------

.. py:function:: build_sort_key(field: str, direction: pypaginate.domain.enums.SortDirection, nulls: pypaginate.domain.enums.NullsPosition) -> collections.abc.Callable[[object], tuple[bool, Any]]

   Build a sort key function for a single field.

   Returns a tuple key ``(is_null_flag, value)`` so that nulls
   sort to the requested position independently of direction.

   :param field: Dotted field path to extract.
   :param direction: ASC or DESC ordering.
   :param nulls: Where to place None values.

   :returns: A callable that produces a sortable tuple from an item.


