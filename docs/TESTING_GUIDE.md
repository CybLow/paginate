# Guide de Test pour PyPaginator 🧪

Ce guide explique comment exécuter, écrire et contribuer aux tests de pypaginator.

## 📋 Table des Matières

- [Installation](#installation)
- [Exécution des Tests](#exécution-des-tests)
- [Couverture des Tests](#couverture-des-tests)
- [Structure des Tests](#structure-des-tests)
- [Écrire de Nouveaux Tests](#écrire-de-nouveaux-tests)
- [Bonnes Pratiques](#bonnes-pratiques)
- [Dépannage](#dépannage)

## 🛠️ Installation

### Dépendances de Base

```bash
# Avec uv (recommandé)
uv pip install -e ".[dev]"

# Avec pip
pip install -e ".[dev]"
```

### Dépendances Optionnelles pour Tests Complets

```bash
# Pour les tests FastAPI
pip install httpx

# Pour les tests async SQLAlchemy
pip install aiosqlite

# Pour les tests de recherche floue
pip install rapidfuzz
```

## 🚀 Exécution des Tests

### Tous les tests

```bash
# Exécution simple
pytest

# Avec verbose
pytest -v

# Parallélisation (plus rapide)
pytest -n auto
```

### Tests spécifiques

```bash
# Un fichier
pytest tests/test_sql_filter_adapter.py

# Une classe
pytest tests/test_sql_filter_adapter.py::TestSqlFilterAdapterBuildCondition

# Un test
pytest tests/test_sql_filter_adapter.py::TestSqlFilterAdapterBuildCondition::test_equals_operator

# Par marqueur (si configuré)
pytest -m unit
pytest -m integration
```

### Tests avec options

```bash
# Arrêter au premier échec
pytest -x

# Montrer les print statements
pytest -s

# Re-exécuter les tests échoués
pytest --lf

# Mode quiet
pytest -q
```

## 📊 Couverture des Tests

### Générer un Rapport de Couverture

```bash
# Rapport terminal
pytest --cov=pypaginator --cov-report=term-missing

# Rapport HTML (recommandé)
pytest --cov=pypaginator --cov-report=html

# Ouvrir le rapport HTML
# Windows
start htmlcov/index.html
# Linux/Mac
open htmlcov/index.html
```

### Couverture d'un Module Spécifique

```bash
pytest tests/test_sql_filter_adapter.py \
    --cov=pypaginator.filters.sql_adapter \
    --cov-report=term-missing
```

### Exiger un Seuil de Couverture

```bash
# Échouer si < 80%
pytest --cov=pypaginator --cov-fail-under=80
```

## 📁 Structure des Tests

```
tests/
├── conftest.py                     # Fixtures partagées
├── test_sql_filter_adapter.py     # Tests SQL adapter
├── test_fastapi_integration.py    # Tests FastAPI
├── test_core.py                   # Tests core
├── test_pages.py                  # Tests pagination
├── test_filter_engine.py          # Tests filtrage
├── test_search.py                 # Tests recherche
└── ...
```

### Conventions de Nommage

- **Fichiers:** `test_<module>.py`
- **Classes:** `Test<ClassName>`
- **Méthodes:** `test_<description_snake_case>`
- **Fixtures:** `<resource_name>` (pas de préfixe test_)

## ✍️ Écrire de Nouveaux Tests

### Template de Base

```python
"""Tests for module X.

This module tests the functionality of X.
"""

from __future__ import annotations

import pytest

from pypaginator.module import ClassToTest


class TestClassName:
    """Tests for ClassName."""

    def test_basic_functionality(self) -> None:
        """Test basic functionality."""
        obj = ClassToTest()
        result = obj.method()
        
        assert result == expected_value

    def test_edge_case(self) -> None:
        """Test edge case."""
        obj = ClassToTest()
        
        with pytest.raises(ValueError):
            obj.method_that_raises()
```

### Utiliser des Fixtures

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return [1, 2, 3, 4, 5]


class TestWithFixture:
    def test_using_fixture(self, sample_data):
        """Test using a fixture."""
        assert len(sample_data) == 5
```

### Tests Paramétrés

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    """Test doubling values."""
    assert double(input) == expected
```

### Tests Async

```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_function()
    assert result == expected
```

### Tests avec Base de Données

```python
@pytest.fixture
def db_session():
    """Create a database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_with_database(db_session):
    """Test database operations."""
    user = User(name="Alice")
    db_session.add(user)
    db_session.commit()
    
    assert db_session.query(User).count() == 1
```

## 🎯 Bonnes Pratiques

### 1. Tests Isolés et Indépendants

✅ **BON:**
```python
def test_addition():
    calculator = Calculator()  # Nouvelle instance
    assert calculator.add(2, 3) == 5
```

❌ **MAUVAIS:**
```python
calculator = Calculator()  # État partagé

def test_addition():
    assert calculator.add(2, 3) == 5  # Dépend de l'état global
```

### 2. Tests Clairs et Descriptifs

✅ **BON:**
```python
def test_paginate_returns_correct_page_count_for_empty_list():
    """Test that pagination handles empty lists correctly."""
    result = paginate([], page=1, limit=10)
    assert result.total == 0
```

❌ **MAUVAIS:**
```python
def test_1():
    """Test."""
    assert paginate([], 1, 10).total == 0
```

### 3. Arrange-Act-Assert (AAA)

```python
def test_user_creation():
    # Arrange
    name = "Alice"
    email = "alice@example.com"
    
    # Act
    user = User(name=name, email=email)
    
    # Assert
    assert user.name == name
    assert user.email == email
```

### 4. Tester les Cas Limites

```python
def test_edge_cases():
    # Empty input
    assert process([]) == []
    
    # Single item
    assert process([1]) == [1]
    
    # Large input
    assert len(process(range(10000))) == 10000
    
    # None input
    with pytest.raises(TypeError):
        process(None)
```

### 5. Mock avec Parcimonie

✅ **BON:** Mocker les dépendances externes (API, DB)
```python
def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "ok"}
    mocker.patch("requests.get", return_value=mock_response)
    
    result = fetch_data()
    assert result["status"] == "ok"
```

❌ **MAUVAIS:** Mocker la logique interne testée
```python
def test_calculation(mocker):
    # Ne teste rien du tout!
    mocker.patch("module.calculate", return_value=42)
    assert calculate() == 42
```

## 📚 Exemples de Tests par Type

### Tests d'Opérateurs SQL

Voir: `tests/test_sql_filter_adapter.py`

```python
def test_equals_operator(self, session: Session) -> None:
    """Test equality operator."""
    condition = SqlFilterAdapter.build_condition(
        Product.category, "eq", "Electronics"
    )
    results = session.execute(
        select(Product).where(condition)
    ).scalars().all()
    
    assert len(results) == 3
    assert all(p.category == "Electronics" for p in results)
```

### Tests d'Intégration FastAPI

Voir: `tests/test_fastapi_integration.py`

```python
def test_endpoint_pagination(self, client: TestClient) -> None:
    """Test pagination endpoint."""
    response = client.get("/items?page=2&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 10
```

### Tests de Pagination

Voir: `tests/test_pages.py`

```python
def test_page_calculation():
    """Test page offset calculation."""
    params = PageParams(page=3, limit=10)
    
    assert params.offset == 20
    assert params.limit == 10
```

## 🔧 Dépannage

### Tests Échouent Localement Mais Passent en CI

1. **Vérifier les versions de dépendances**
   ```bash
   pip list | grep pytest
   ```

2. **Nettoyer le cache pytest**
   ```bash
   pytest --cache-clear
   ```

3. **Réinstaller les dépendances**
   ```bash
   pip install -e ".[dev]" --force-reinstall
   ```

### Import Errors

Si vous voyez `ModuleNotFoundError`:

1. **Vérifier l'installation en mode éditable**
   ```bash
   pip install -e .
   ```

2. **Vérifier PYTHONPATH**
   ```bash
   echo $PYTHONPATH  # Linux/Mac
   echo %PYTHONPATH%  # Windows
   ```

### Tests Lents

1. **Utiliser pytest-xdist pour paralléliser**
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

2. **Désactiver la couverture durant le développement**
   ```bash
   pytest  # Sans --cov
   ```

3. **Exécuter uniquement les tests modifiés**
   ```bash
   pytest --lf  # Last failed
   pytest --nf  # New first
   ```

### Erreurs de Dépendances Optionnelles

Certains tests nécessitent des dépendances optionnelles:

```python
# Skip si non disponible
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
```

Pour installer toutes les dépendances:
```bash
pip install pypaginator[fastapi,fuzzy]
```

## 📈 Améliorer la Couverture

### Trouver les Lignes Non Testées

```bash
pytest --cov=pypaginator --cov-report=term-missing | grep "TOTAL"
```

### Générer un Rapport HTML Détaillé

```bash
pytest --cov=pypaginator --cov-report=html
start htmlcov/index.html  # Ouvre dans le navigateur
```

### Prioriser les Modules

1. Vérifier la couverture actuelle
2. Identifier les modules < 70%
3. Commencer par les modules critiques (core, filters, engines)
4. Voir `docs/TEST_COVERAGE_ANALYSIS.md` pour le plan complet

## 🤝 Contribuer

### Checklist pour Nouveaux Tests

- [ ] Tests suivent les conventions de nommage
- [ ] Docstrings clairs et descriptifs
- [ ] Tests isolés et indépendants
- [ ] Cas limites couverts
- [ ] Cas d'erreur testés
- [ ] Fixtures utilisées quand approprié
- [ ] Type hints ajoutés
- [ ] Tests passent localement (`pytest -v`)
- [ ] Couverture vérifiée (`pytest --cov`)
- [ ] Documentation mise à jour si nécessaire

### Soumettre des Tests

1. Créer une branche: `git checkout -b test/module-name`
2. Écrire les tests
3. Vérifier la couverture: `pytest --cov`
4. Commit: `git commit -m "test: add tests for module X"`
5. Push et créer une PR

## 📖 Ressources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

## 🆘 Besoin d'Aide?

- Voir les exemples dans `tests/`
- Consulter `docs/TEST_COVERAGE_ANALYSIS.md`
- Ouvrir une issue sur GitHub
- Rejoindre les discussions

---

**Dernière mise à jour:** 2025-12-23  
**Version:** 1.0  
**Mainteneur:** PyPaginator Team

