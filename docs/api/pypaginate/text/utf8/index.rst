pypaginate.text.utf8
====================

.. py:module:: pypaginate.text.utf8

.. autoapi-nested-parse::

   UTF-8 normalization and ASCII transliteration primitives.



Attributes
----------

.. autoapisummary::

   pypaginate.text.utf8.NormalizationForm


Classes
-------

.. autoapisummary::

   pypaginate.text.utf8.Utf8Normalizer


Functions
---------

.. autoapisummary::

   pypaginate.text.utf8.create_search_normalizer
   pypaginate.text.utf8.normalize_utf8
   pypaginate.text.utf8.transliterate_ascii


Module Contents
---------------

.. py:class:: Utf8Normalizer

   UTF-8 text normalizer with configurable casing and normalization form.


   .. py:method:: normalise(value: str) -> str

      Normalize the given UTF-8 string.

      :param value: Input text to normalize.

      :returns: The normalized string according to the instance configuration.



.. py:function:: create_search_normalizer() -> Utf8Normalizer

   Return the canonical search normalizer (lowercase + NFKC).

   :returns: A configured Utf8Normalizer instance.


.. py:function:: normalize_utf8(value: str, *, lowercase: bool, casefold_output: bool, form: NormalizationForm) -> str

   Normalize a UTF-8 string with specified casing and form.

   :param value: Input text to normalize.
   :param lowercase: Whether to lowercase the result (ignored if casefold_output).
   :param casefold_output: Whether to apply casefolding for aggressive matching.
   :param form: Unicode normalization form (e.g. "NFKC").

   :returns: The normalized string.


.. py:function:: transliterate_ascii(value: str) -> str

   Return ASCII transliteration using text-unidecode.

   :param value: Input unicode text.

   :returns: ASCII-only transliteration of value.


.. py:data:: NormalizationForm

   Literal type for Unicode normalization forms.

