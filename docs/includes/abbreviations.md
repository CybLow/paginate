<!-- Glossary of terms - auto-appended to all pages via pymdownx.snippets -->
<!-- These create hover tooltips when terms appear in documentation -->

<!-- Pagination Terms -->
*[offset pagination]: Traditional pagination using LIMIT/OFFSET, simple but slow for large datasets
*[keyset pagination]: Cursor-based pagination using WHERE clauses, faster for large datasets
*[cursor pagination]: Alias for keyset pagination, uses encoded cursors for stateless navigation
*[cursor]: An encoded token representing a position in a result set for keyset pagination
*[page token]: A cursor that can be passed to fetch the next or previous page of results

<!-- Database Terms -->
*[ORM]: Object-Relational Mapping, a technique for converting data between type systems
*[SQLAlchemy]: Python SQL toolkit and ORM, the primary database adapter for pypaginate
*[N+1 problem]: Database anti-pattern where N additional queries are made for N results
*[collation]: Database rules for string comparison and sorting (case sensitivity, accents)

<!-- Filter Terms -->
*[JSONLogic]: A JSON-based format for describing filter logic with operators
*[predicate]: A function that returns true or false, used for filtering
*[filter engine]: The component that evaluates filter expressions against data

<!-- Search Terms -->
*[fuzzy search]: Search that finds approximate matches, tolerating typos and variations
*[Levenshtein distance]: A metric measuring the minimum edits to transform one string into another
*[trigram]: A sequence of three consecutive characters, used for similarity matching
*[relevance score]: A numeric score indicating how well a result matches a search query

<!-- Architecture Terms -->
*[paginator]: A component that divides data into discrete pages
*[executor]: A component that runs queries against a data source
*[adapter]: A component that translates between different interfaces
*[protocol]: A Python typing construct defining an interface (similar to interface in other languages)

<!-- Python Terms -->
*[async]: Asynchronous programming, allowing concurrent execution without blocking
*[await]: Python keyword to wait for an async operation to complete
*[generator]: A function that yields values lazily, one at a time
*[dataclass]: A Python decorator that auto-generates boilerplate for data-holding classes
*[Pydantic]: Python library for data validation using type annotations

<!-- Framework Terms -->
*[FastAPI]: Modern Python web framework for building APIs with automatic OpenAPI docs
*[dependency injection]: Design pattern where dependencies are provided rather than created
*[middleware]: Code that runs between request and response in a web framework

<!-- General Terms -->
*[API]: Application Programming Interface
*[CRUD]: Create, Read, Update, Delete - basic data operations
*[REST]: Representational State Transfer, an architectural style for web APIs
*[UUID]: Universally Unique Identifier, a 128-bit identifier
