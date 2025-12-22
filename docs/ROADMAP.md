# PyPaginator - Roadmap vers la Parité Complète

**Version actuelle:** 0.1.0  
**Objectif:** Couvrir 100% des fonctionnalités de fastapi-pagination et fastapi-filters

---

## 🎯 Versions Planifiées

### v0.2.0 - Intégration FastAPI Déclarative (Q1 2025)
**Date cible:** 8 semaines  
**Focus:** Filtrage déclaratif et dépendances

### v0.3.0 - Formats de Pagination Multiples (Q1 2025)
**Date cible:** 4 semaines  
**Focus:** Flexibilité et compatibilité

### v0.4.0 - Optimisations et Relations (Q2 2025)
**Date cible:** 6 semaines  
**Focus:** Performance et fonctionnalités avancées

### v1.0.0 - Production Ready (Q2 2025)
**Date cible:** 4 semaines  
**Focus:** Stabilisation et documentation

---

## 📋 v0.2.0 - Intégration FastAPI Déclarative

### Objectifs

✅ Atteindre parité avec fastapi-filters pour l'intégration FastAPI  
✅ Rendre PyPaginator production-ready pour 80% des cas d'usage  
✅ Simplifier drastiquement le code utilisateur

### Issues Critiques

#### 1. Système de Filtres Déclaratifs

**Fichier:** `src/pypaginator/integrations/filters.py` (NOUVEAU)

```python
"""Declarative filtering system for FastAPI."""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field, create_model
from fastapi import Query, Depends

T = TypeVar('T')

class FilterField:
    """Descriptor for filter fields with operators.
    
    Example:
        name: str | None = FilterField(None, operator='ilike')
        age: int | None = FilterField(None, operator='gte')
    """
    
    def __init__(
        self,
        default: Any = None,
        *,
        operator: str = 'eq',
        alias: str | None = None,
        description: str | None = None,
    ):
        self.default = default
        self.operator = operator
        self.alias = alias
        self.description = description

class FilterModel(BaseModel):
    """Base class for declarative filter models.
    
    Example:
        class UserFilter(FilterModel):
            name: str | None = FilterField(None, operator='ilike')
            age: int | None = FilterField(None, operator='gte')
            
            class Config:
                model = User
    """
    
    class Config:
        model: type | None = None
        
    def to_sql_conditions(self) -> list[ColumnElement[bool]]:
        """Convert filter model to SQLAlchemy conditions."""
        ...
        
    def to_json_logic(self) -> dict[str, Any]:
        """Convert filter model to JSON Logic format."""
        ...

def FilterDepends(
    filter_class: type[FilterModel],
    *,
    alias_generator: Callable[[str], str] | None = None,
) -> Callable:
    """Create FastAPI dependency for filter model.
    
    Usage:
        @app.get("/users")
        async def list_users(
            filters: UserFilter = FilterDepends(UserFilter),
            pagination: PageParams = Depends(get_pagination_params),
        ):
            stmt = select(User).where(*filters.to_sql_conditions())
            return await paginate_entities(session, stmt, pagination)
    """
    ...
```

**Tests:** `tests/integrations/test_filters.py`

**Estimation:** 2 semaines

---

#### 2. Auto SQL WHERE Generation

**Fichier:** `src/pypaginator/filters/sql_adapter.py` (AMÉLIORER)

```python
"""Enhanced SQL adapter with relation support."""

from sqlalchemy import and_, or_
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty
from typing import Any

class SqlFilterAdapter:
    """Build SQLAlchemy conditions from FilterModel."""
    
    def __init__(self, model_class: type):
        self.model_class = model_class
        self._relation_cache: dict[str, list[str]] = {}
        
    def build_where_clause(
        self, 
        filter_model: FilterModel
    ) -> list[ColumnElement[bool]]:
        """Convert entire FilterModel to WHERE conditions.
        
        Handles:
        - Simple fields (user.name = 'John')
        - Nested fields (user.profile.bio like '%dev%')
        - Relations (user.posts.title contains 'Python')
        """
        conditions = []
        
        for field_name, field_value in filter_model.model_dump(exclude_none=True).items():
            if field_value is None:
                continue
                
            field_def = filter_model.model_fields[field_name]
            operator = getattr(field_def, 'operator', 'eq')
            
            # Handle nested fields (profile__bio)
            if '__' in field_name:
                condition = self._build_relation_condition(
                    field_name, operator, field_value
                )
            else:
                column = getattr(self.model_class, field_name)
                condition = self.build_condition(column, operator, field_value)
            
            conditions.append(condition)
        
        return conditions
    
    def _build_relation_condition(
        self,
        path: str,
        operator: str,
        value: Any,
    ) -> ColumnElement[bool]:
        """Build condition for related field with auto-join.
        
        Example:
            posts__title__ilike='%python%'
            → JOIN posts ON ... WHERE posts.title ILIKE '%python%'
        """
        ...
        
    def get_required_joins(
        self,
        filter_model: FilterModel
    ) -> list[tuple[type, type]]:
        """Extract required JOIN clauses from filter model.
        
        Returns:
            List of (parent_model, related_model) tuples
        """
        ...
```

**Tests:** `tests/filters/test_sql_adapter_advanced.py`

**Estimation:** 1.5 semaines

---

#### 3. OrderingDepends

**Fichier:** `src/pypaginator/integrations/ordering.py` (NOUVEAU)

```python
"""Declarative ordering for FastAPI."""

from fastapi import Query
from typing import Annotated

class OrderingParams:
    """Validated ordering parameters.
    
    Attributes:
        sort_by: List of fields to sort by
        order: 'asc' or 'desc'
    """
    
    def __init__(
        self,
        sort_by: list[str],
        order: list[str] | None = None,
        *,
        allowed_fields: list[str],
    ):
        self.sort_by = sort_by
        self.order = order or ['asc'] * len(sort_by)
        self._validate(allowed_fields)
        
    def _validate(self, allowed_fields: list[str]):
        """Validate sort fields against whitelist."""
        for field in self.sort_by:
            clean_field = field.lstrip('-')
            if clean_field not in allowed_fields:
                raise ValidationException(
                    f"Field '{clean_field}' is not allowed for sorting"
                )
    
    def to_sql_order_by(self, model_class: type) -> list[ColumnElement]:
        """Convert to SQLAlchemy ORDER BY clauses."""
        ...

def OrderingDepends(
    allowed_fields: list[str],
    *,
    default: list[str] | None = None,
) -> Callable:
    """Create FastAPI dependency for ordering.
    
    Usage:
        @app.get("/users")
        async def list_users(
            ordering: OrderingParams = OrderingDepends(
                allowed_fields=['name', 'created_at', 'age'],
                default=['created_at'],
            ),
        ):
            stmt = select(User).order_by(*ordering.to_sql_order_by(User))
            ...
    
    Query params:
        ?sort_by=name,-created_at  # name ASC, created_at DESC
        ?sort_by=age&order=desc    # age DESC
    """
    
    def dependency(
        sort_by: Annotated[list[str], Query()] = default or [],
        order: Annotated[list[str] | None, Query()] = None,
    ) -> OrderingParams:
        return OrderingParams(
            sort_by=sort_by,
            order=order,
            allowed_fields=allowed_fields,
        )
    
    return dependency
```

**Tests:** `tests/integrations/test_ordering.py`

**Estimation:** 1 semaine

---

#### 4. Relations et Auto-Join

**Fichier:** `src/pypaginator/filters/relations.py` (NOUVEAU)

```python
"""Relation resolver for automatic JOINs."""

from sqlalchemy import select
from sqlalchemy.orm import RelationshipProperty, InspectionMixin
from typing import Any

class RelationResolver:
    """Resolve relationship paths and build JOIN clauses.
    
    Example:
        resolver = RelationResolver(User)
        joins = resolver.resolve_path('posts__author__profile')
        # Returns: [User.posts, Post.author, Author.profile]
    """
    
    def __init__(self, model_class: type):
        self.model_class = model_class
        self._relationship_cache: dict[str, RelationshipProperty] = {}
        self._inspect_relationships()
    
    def _inspect_relationships(self):
        """Cache all relationships for the model."""
        mapper = inspect(self.model_class)
        for rel in mapper.relationships:
            self._relationship_cache[rel.key] = rel
    
    def resolve_path(self, path: str) -> list[InstrumentedAttribute]:
        """Resolve relationship path to list of joinable attributes.
        
        Args:
            path: Double-underscore separated path (e.g., 'posts__author')
        
        Returns:
            List of SQLAlchemy relationship attributes to join
        
        Raises:
            RelationNotFound: If any part of path doesn't exist
        """
        parts = path.split('__')
        current_model = self.model_class
        joins = []
        
        for part in parts[:-1]:  # Last part is the field, not a relation
            if part not in self._relationship_cache:
                raise RelationNotFound(
                    f"Relation '{part}' not found on {current_model.__name__}"
                )
            
            rel = self._relationship_cache[part]
            joins.append(getattr(current_model, part))
            current_model = rel.mapper.class_
            
            # Update cache for next model
            self._relationship_cache = {}
            for r in inspect(current_model).relationships:
                self._relationship_cache[r.key] = r
        
        return joins
    
    def get_target_column(self, path: str) -> InstrumentedAttribute:
        """Get the final column from a relationship path.
        
        Args:
            path: Path like 'posts__title'
        
        Returns:
            The actual column (e.g., Post.title)
        """
        parts = path.split('__')
        
        if len(parts) == 1:
            return getattr(self.model_class, path)
        
        # Navigate to target model
        current_model = self.model_class
        for part in parts[:-1]:
            rel = inspect(current_model).relationships[part]
            current_model = rel.mapper.class_
        
        # Return final column
        return getattr(current_model, parts[-1])

def apply_joins(
    stmt: Select,
    filter_model: FilterModel,
) -> Select:
    """Automatically add required JOINs to statement.
    
    Usage:
        stmt = select(User)
        stmt = apply_joins(stmt, user_filter)
        # JOINs added automatically based on filter fields
    """
    resolver = RelationResolver(filter_model.Config.model)
    
    for field_name in filter_model.model_fields:
        if '__' in field_name:
            joins = resolver.resolve_path(field_name)
            for join_attr in joins:
                stmt = stmt.join(join_attr)
    
    return stmt
```

**Tests:** `tests/filters/test_relations.py`

**Estimation:** 1.5 semaines

---

#### 5. Améliorer Intégration FastAPI

**Fichier:** `src/pypaginator/integrations/fastapi.py` (AMÉLIORER)

Ajouter:
- Support pour response_model avec filtres
- Génération OpenAPI complète
- Exemples dans la doc API

**Fichier:** `src/pypaginator/dependencies.py` (SUPPRIMER)

Fusionner tout dans `integrations/fastapi.py`

**Estimation:** 3 jours

---

### Exemples de la v0.2.0

#### Avant (v0.1.0) - Code utilisateur verbeux

```python
@app.get("/users")
async def list_users(
    session: AsyncSession = Depends(get_session),
    params: PageParams = Depends(get_pagination_params),
    # Filtres manuels 😢
    name: str | None = None,
    min_age: int | None = None,
    email: str | None = None,
    sort_by: str = 'created_at',
):
    # Construction manuelle de la requête
    stmt = select(User)
    
    # Filtres manuels
    if name:
        stmt = stmt.where(User.name.ilike(f'%{name}%'))
    if min_age:
        stmt = stmt.where(User.age >= min_age)
    if email:
        stmt = stmt.where(User.email == email)
    
    # Tri manuel
    if sort_by == 'name':
        stmt = stmt.order_by(User.name)
    elif sort_by == 'created_at':
        stmt = stmt.order_by(User.created_at)
    
    # Pagination
    page = await paginate_entities(session, stmt, params)
    return page
```

#### Après (v0.2.0) - Code déclaratif ✨

```python
class UserFilter(FilterModel):
    name: str | None = FilterField(None, operator='ilike')
    min_age: int | None = FilterField(None, operator='gte', alias='age')
    email: str | None = FilterField(None, operator='eq')
    
    class Config:
        model = User

@app.get("/users")
async def list_users(
    session: AsyncSession = Depends(get_session),
    filters: UserFilter = FilterDepends(UserFilter),
    ordering: OrderingParams = OrderingDepends(['name', 'created_at', 'age']),
    pagination: PageParams = Depends(get_pagination_params),
):
    stmt = (
        select(User)
        .where(*filters.to_sql_conditions())
        .order_by(*ordering.to_sql_order_by(User))
    )
    return await paginate_entities(session, stmt, pagination)
```

**Réduction:** ~30 lignes → ~15 lignes  
**Lisibilité:** +300%  
**Maintenabilité:** +500%

---

### Checklist v0.2.0

- [ ] Créer `FilterField` descriptor
- [ ] Créer `FilterModel` base class
- [ ] Implémenter `FilterDepends` dependency
- [ ] Améliorer `SqlFilterAdapter.build_where_clause()`
- [ ] Créer `RelationResolver` pour auto-joins
- [ ] Implémenter `apply_joins()` helper
- [ ] Créer `OrderingParams` et `OrderingDepends`
- [ ] Tests complets pour filtres déclaratifs
- [ ] Tests complets pour relations
- [ ] Tests complets pour ordering
- [ ] Exemples dans documentation
- [ ] Migration guide v0.1 → v0.2
- [ ] CHANGELOG.md mis à jour
- [ ] Supprimer `dependencies.py` (fusionner)

---

## 📋 v0.3.0 - Formats de Pagination Multiples

### Objectifs

✅ Supporter plusieurs formats de pagination  
✅ Compatibilité avec fastapi-pagination  
✅ Personnalisation flexible

### Issues

#### 1. Page Formats Alternatifs

**Fichier:** `src/pypaginator/core/formats.py` (NOUVEAU)

```python
"""Alternative pagination formats."""

from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class LimitOffsetPage(Generic[T]):
    """Pagination with limit/offset instead of page/limit.
    
    Common in APIs that expose database concepts directly.
    """
    items: Sequence[T]
    total: int
    limit: int
    offset: int
    
    @classmethod
    def from_page(cls, page: Page[T]) -> 'LimitOffsetPage[T]':
        """Convert from standard Page format."""
        return cls(
            items=page.items,
            total=page.total,
            limit=page.limit,
            offset=(page.page - 1) * page.limit,
        )

@dataclass(frozen=True, slots=True)
class CursorPage(Generic[T]):
    """Cursor-based pagination response.
    
    Uses opaque tokens instead of page numbers.
    """
    items: Sequence[T]
    next_cursor: str | None
    prev_cursor: str | None
    has_next: bool
    has_previous: bool

@dataclass(frozen=True, slots=True)
class PageWithLinks(Generic[T]):
    """Page with HATEOAS navigation links."""
    items: Sequence[T]
    total: int
    page: int
    limit: int
    links: PaginationLinks
    
@dataclass(frozen=True, slots=True)
class PaginationLinks:
    """HATEOAS links for pagination."""
    first: str
    last: str
    next: str | None
    prev: str | None
    self: str
```

**Estimation:** 1 semaine

---

#### 2. Params Factory

**Fichier:** `src/pypaginator/core/params_factory.py` (NOUVEAU)

```python
"""Factory for custom pagination parameters."""

from typing import Callable
from fastapi import Query

class PageParamsFactory:
    """Create custom pagination parameter dependencies.
    
    Example:
        # Custom names
        get_params = PageParamsFactory(
            page_name='offset',
            limit_name='count',
        ).create()
        
        # Custom validation
        get_params = PageParamsFactory(
            max_limit=50,
            default_limit=10,
        ).create()
    """
    
    def __init__(
        self,
        *,
        page_name: str = 'page',
        limit_name: str = 'limit',
        default_page: int = 1,
        default_limit: int = 20,
        max_limit: int = 100,
    ):
        self.page_name = page_name
        self.limit_name = limit_name
        self.default_page = default_page
        self.default_limit = default_limit
        self.max_limit = max_limit
    
    def create(self) -> Callable[..., PageParams]:
        """Create FastAPI dependency function."""
        
        def get_params(
            page: int = Query(
                self.default_page,
                ge=1,
                alias=self.page_name,
            ),
            limit: int = Query(
                self.default_limit,
                ge=1,
                le=self.max_limit,
                alias=self.limit_name,
            ),
        ) -> PageParams:
            return PageParams(page=page, limit=limit)
        
        return get_params
```

**Estimation:** 3 jours

---

#### 3. Link Generator

**Fichier:** `src/pypaginator/core/links.py` (NOUVEAU)

```python
"""Generate HATEOAS pagination links."""

from urllib.parse import urlencode

class LinkGenerator:
    """Generate pagination navigation links.
    
    Example:
        generator = LinkGenerator(base_url='/api/users')
        links = generator.generate(page=2, limit=20, total=100)
        # links.next = '/api/users?page=3&limit=20'
    """
    
    def __init__(
        self,
        base_url: str,
        *,
        query_params: dict[str, Any] | None = None,
    ):
        self.base_url = base_url
        self.query_params = query_params or {}
    
    def generate(
        self,
        page: int,
        limit: int,
        total: int,
    ) -> PaginationLinks:
        """Generate all pagination links."""
        total_pages = (total + limit - 1) // limit
        
        return PaginationLinks(
            first=self._build_link(1, limit),
            last=self._build_link(total_pages, limit),
            next=self._build_link(page + 1, limit) if page < total_pages else None,
            prev=self._build_link(page - 1, limit) if page > 1 else None,
            self=self._build_link(page, limit),
        )
    
    def _build_link(self, page: int, limit: int) -> str:
        """Build single link with query parameters."""
        params = {
            **self.query_params,
            'page': page,
            'limit': limit,
        }
        return f"{self.base_url}?{urlencode(params)}"
```

**Estimation:** 2 jours

---

### Checklist v0.3.0

- [ ] Créer tous les formats alternatifs
- [ ] Implémenter `PageParamsFactory`
- [ ] Créer `LinkGenerator`
- [ ] Ajouter converters entre formats
- [ ] Tests pour chaque format
- [ ] Documentation des formats
- [ ] Migration guide
- [ ] CHANGELOG.md

---

## 📋 v0.4.0 - Optimisations et Relations

### Objectifs

✅ Performance optimale  
✅ Relations complexes  
✅ Opérateurs avancés

### Issues

#### 1. Count Query Caching

**Fichier:** `src/pypaginator/query/cache.py` (NOUVEAU)

```python
"""Count query result caching."""

from functools import lru_cache
import hashlib

class CountCache:
    """Cache count query results."""
    
    def __init__(self, ttl: int = 60):
        self.ttl = ttl
        self._cache: dict[str, tuple[int, float]] = {}
    
    def get(self, query_hash: str) -> int | None:
        """Get cached count if valid."""
        ...
    
    def set(self, query_hash: str, count: int):
        """Cache count result."""
        ...
```

**Estimation:** 1 semaine

---

#### 2. Opérateurs SQL Avancés

Étendre `SqlFilterAdapter`:

```python
# Nouveaux opérateurs
case "between":
    return column.between(value[0], value[1])
case "array_contains":
    return column.contains(value)
case "jsonb_path":
    return column.op('?')(value)
case "full_text_search":
    return func.to_tsvector(column).op('@@')(func.plainto_tsquery(value))
```

**Estimation:** 1 semaine

---

#### 3. Relations Complexes

Support pour:
- Many-to-many
- Polymorphic relations
- Self-referential

**Estimation:** 2 semaines

---

### Checklist v0.4.0

- [ ] Implémenter count caching
- [ ] Ajouter opérateurs avancés
- [ ] Support M2M relations
- [ ] Benchmarks de performance
- [ ] Documentation optimisations
- [ ] CHANGELOG.md

---

## 📋 v1.0.0 - Production Ready

### Objectifs

✅ 100% test coverage  
✅ Documentation complète  
✅ API stable

### Checklist

- [ ] Test coverage >95%
- [ ] Documentation exhaustive
- [ ] Migration guides
- [ ] Benchmarks publiés
- [ ] Versioning sémantique
- [ ] Security audit
- [ ] Performance profiling
- [ ] Real-world examples
- [ ] API finalisée (no breaking changes)

---

## 📊 Métriques de Succès

### v0.2.0
- [ ] 80% cas d'usage couverts
- [ ] Réduction 50% lignes de code utilisateur
- [ ] 100% tests passing

### v0.3.0
- [ ] 3+ formats pagination
- [ ] Compatibilité fastapi-pagination

### v0.4.0
- [ ] Count queries 10x plus rapides (avec cache)
- [ ] Support 20+ relations complexes

### v1.0.0
- [ ] >95% test coverage
- [ ] <5 issues critiques ouvertes
- [ ] 10+ projets en production

---

## 🚀 Comment Contribuer

Voir `CONTRIBUTING.md` pour les guidelines.

Priorités actuelles:
1. v0.2.0 - FilterModel et FilterDepends
2. Tests d'intégration FastAPI
3. Documentation exemples

---

## 📅 Timeline

```
2025 Q1
├── Semaine 1-2:   FilterModel + FilterField
├── Semaine 3-4:   SqlFilterAdapter + Relations
├── Semaine 5-6:   OrderingDepends
├── Semaine 7-8:   Tests + Documentation
└── Release v0.2.0

2025 Q1-Q2
├── Semaine 9-10:  Formats alternatifs
├── Semaine 11-12: Links + Customizers
└── Release v0.3.0

2025 Q2
├── Semaine 13-16: Optimisations
├── Semaine 17-18: Relations complexes
└── Release v0.4.0

2025 Q2
├── Semaine 19-20: Stabilisation
├── Semaine 21-22: Documentation finale
└── Release v1.0.0 🎉
```

