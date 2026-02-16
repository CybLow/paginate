pypaginate.exceptions
=====================

.. py:module:: pypaginate.exceptions

.. autoapi-nested-parse::

   Exceptions for pypaginate.

   This module defines all custom exceptions used by the pagination system.



Exceptions
----------

.. autoapisummary::

   pypaginate.exceptions.FilterException
   pypaginate.exceptions.FilterValidationError
   pypaginate.exceptions.PaginationConfigurationError
   pypaginate.exceptions.PaginatorException
   pypaginate.exceptions.SearchException
   pypaginate.exceptions.SearchNormalizationError
   pypaginate.exceptions.SearchQueryError
   pypaginate.exceptions.SortException
   pypaginate.exceptions.ValidationException


Module Contents
---------------

.. py:exception:: FilterException(message: str, field: str | None = None)

   Bases: :py:obj:`PaginatorException`


   Raised when filtering operations fail.


.. py:exception:: FilterValidationError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`FilterException`


   Raised when filter validation fails.


.. py:exception:: PaginationConfigurationError(message: str, *, field: str | None = None, value: object = None, reason: str | None = None, details: dict[str, Any] | None = None)

   Bases: :py:obj:`PaginatorException`


   Raised when pagination configuration is invalid.


.. py:exception:: PaginatorException

   Bases: :py:obj:`Exception`


   Base exception for all pypaginate errors.


.. py:exception:: SearchException

   Bases: :py:obj:`PaginatorException`


   Raised when search operations fail.


.. py:exception:: SearchNormalizationError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`SearchException`


   Raised when text normalization for search fails.


.. py:exception:: SearchQueryError(message: str, *, details: dict[str, Any] | None = None)

   Bases: :py:obj:`SearchException`


   Raised when search query processing fails.


.. py:exception:: SortException

   Bases: :py:obj:`PaginatorException`


   Raised when sort operations fail.


.. py:exception:: ValidationException(field: str, value: object, reason: str)

   Bases: :py:obj:`PaginatorException`


   Raised when validation fails.


