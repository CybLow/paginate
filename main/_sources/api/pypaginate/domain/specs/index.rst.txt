pypaginate.domain.specs
=======================

.. py:module:: pypaginate.domain.specs

.. autoapi-nested-parse::

   User-facing specification objects for filtering, sorting, and search.

   Specs are immutable Pydantic models that users construct to describe
   what they want. Engines consume specs to execute the operations.



Attributes
----------

.. autoapisummary::

   pypaginate.domain.specs.FilterInput
   pypaginate.domain.specs.FilterOperator


Classes
-------

.. autoapisummary::

   pypaginate.domain.specs.FilterGroup
   pypaginate.domain.specs.FilterSpec
   pypaginate.domain.specs.SearchSpec
   pypaginate.domain.specs.SortSpec


Functions
---------

.. autoapisummary::

   pypaginate.domain.specs.And
   pypaginate.domain.specs.Or


Module Contents
---------------

.. py:class:: FilterGroup(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Composite filter for nested AND/OR expressions.

   Use ``And()`` and ``Or()`` builder functions instead of
   constructing directly.

   Example::

       And(
           Or(FilterSpec(field="a", value=1), FilterSpec(field="b", value=2)),
           Or(FilterSpec(field="c", value=3), FilterSpec(field="d", value=4)),
       )
       # = (a=1 OR b=2) AND (c=3 OR d=4)


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: FilterSpec(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Declarative filter specification.

   Example::

       FilterSpec(field="age", operator="gte", value=18)
       FilterSpec(field="name", operator="contains", value="john")


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: SearchSpec(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Declarative search specification.

   Example::

       SearchSpec(query="john doe", fields=("name", "email"))
       SearchSpec(query="jhn", fields=("name",), fuzzy=FuzzyMode.FUZZY)
       SearchSpec(query="alice", fields=("name", "bio"), weights={"name": 2.0})


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:class:: SortSpec(/, **data: Any)

   Bases: :py:obj:`pydantic.BaseModel`


   Declarative sort specification.

   Example::

       SortSpec(field="name")
       SortSpec(field="created_at", direction=SortDirection.DESC)


   .. py:attribute:: model_config

      Configuration for the model, should be a dictionary conforming to [`ConfigDict`][pydantic.config.ConfigDict].


.. py:function:: And(*conditions: FilterSpec | FilterGroup) -> FilterGroup

   Create an AND group of filter conditions.


.. py:function:: Or(*conditions: FilterSpec | FilterGroup) -> FilterGroup

   Create an OR group of filter conditions.


.. py:data:: FilterInput

   Type alias for filter input accepted by engines and pipelines.

.. py:data:: FilterOperator

   Supported filter operator names (type-checked at definition time).

