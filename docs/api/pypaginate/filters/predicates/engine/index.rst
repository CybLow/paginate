pypaginate.filters.predicates.engine
====================================

.. py:module:: pypaginate.filters.predicates.engine

.. autoapi-nested-parse::

   Compile filtering specifications into executable predicates.



Classes
-------

.. autoapisummary::

   pypaginate.filters.predicates.engine.CompiledFilter
   pypaginate.filters.predicates.engine.FilterEngine


Functions
---------

.. autoapisummary::

   pypaginate.filters.predicates.engine.filter_items


Module Contents
---------------

.. py:class:: CompiledFilter

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Pair a field accessor with its predicate.


   .. py:method:: matches(item: ItemT) -> bool

      Return True when item matches the predicate.

      :param item: Item to evaluate against the filter.

      :returns: True if the item passes the filter predicate.



   .. py:attribute:: accessor
      :type:  pypaginate.filters.predicates.field_accessor.FieldAccessor

      Accessor resolving field values on items.


   .. py:attribute:: predicate
      :type:  pypaginate.filters.predicates.registry.FilterPredicate[object]

      Callable evaluating the resolved value.


.. py:class:: FilterEngine(registry: pypaginate.filters.predicates.registry.OperatorRegistry[object] | None = None)

   Bases: :py:obj:`Generic`\ [\ :py:obj:`ItemT`\ ]


   Compile declarative filter specifications into callables.


   .. py:method:: apply(items: collections.abc.Sequence[ItemT], filters: collections.abc.Mapping[str, object]) -> list[ItemT]

      Filter items using a mapping of path -> filter spec.

      :param items: Sequence of items to filter.
      :param filters: Mapping of field paths to filter specifications.

      :returns: List of items matching all filter criteria.



.. py:function:: filter_items(items: collections.abc.Sequence[ItemT], filters: collections.abc.Mapping[str, object], *, registry: pypaginate.filters.predicates.registry.OperatorRegistry[object] | None = None) -> list[ItemT]

   Apply declarative filters to an in-memory sequence.

   :param items: Sequence of candidate items to filter.
   :param filters: Mapping of ``path -> filter`` specifications.
   :param registry: Optional operator registry (default operators otherwise).

   :returns: Filtered list of items matching all compiled predicates.


