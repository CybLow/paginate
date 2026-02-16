pypaginate.engines.memory
=========================

.. py:module:: pypaginate.engines.memory

.. autoapi-nested-parse::

   In-memory pagination engine.

   This module provides pagination for in-memory data with support for:
   - Sequence slicing for efficient pagination
   - Streaming iterables with filtering
   - Predicate-based filtering

   Classes
   -------
   MemoryPaginator
       Paginate sequences or iterables while preserving streaming semantics.

   Functions
   ---------
   filter_iter
       Yield items that satisfy an optional predicate.



Classes
-------

.. autoapisummary::

   pypaginate.engines.memory.MemoryPaginator
   pypaginate.engines.memory.SliceBounds


Functions
---------

.. autoapisummary::

   pypaginate.engines.memory.collect_window
   pypaginate.engines.memory.compute_bounds
   pypaginate.engines.memory.filter_iter


Module Contents
---------------

.. py:class:: MemoryPaginator(*, clamp: bool = False)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`T`\ ]


   Paginate sequences or iterables while preserving streaming semantics.


   .. py:method:: paginate(items: collections.abc.Iterable[T], params: pypaginate.core.PageParams, predicate: collections.abc.Callable[[T], bool] | None = None) -> pypaginate.core.Page[T]

      Paginate a sequence or iterable.

      :param items: Iterable of items to paginate.
      :param params: Page parameters.
      :param predicate: Optional filter predicate.

      :returns: A Page object with the requested window.



.. py:class:: SliceBounds

   Represent the half-open slice collected for a page.

   .. attribute:: start

      Starting offset for the slice.

   .. attribute:: end

      Ending offset for the slice (exclusive).


.. py:function:: collect_window(items: collections.abc.Iterator[T], bounds: SliceBounds) -> tuple[list[T], int]

   Collect items falling within the provided bounds and return the total size.

   :param items: Iterator of items to collect from.
   :param bounds: Slice bounds defining the window.

   :returns: Tuple of (collected_items, total_count).


.. py:function:: compute_bounds(params: pypaginate.core.PageParams) -> SliceBounds

   Compute the start/end offsets for the requested page.

   :param params: Page parameters with page number and limit.

   :returns: SliceBounds with start and end offsets.


.. py:function:: filter_iter(items: collections.abc.Iterable[T], predicate: collections.abc.Callable[[T], bool] | None) -> collections.abc.Iterator[T]

   Yield items that satisfy an optional predicate.

   :param items: Iterable of items to iterate over.
   :param predicate: Optional predicate applied to each item.

   :returns: An iterator yielding items for which ``predicate(item)`` is ``True``.
             When ``predicate`` is ``None``, yields all items.


