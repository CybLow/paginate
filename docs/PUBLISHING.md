# Guide de Publication sur PyPI

Ce guide explique comment publier PyPaginator sur PyPI (Python Package Index).

## Prérequis

1. **Compte PyPI** : Créez un compte sur https://pypi.org/account/register/
2. **Compte Test PyPI** (optionnel) : https://test.pypi.org/account/register/
3. **Outils de build** : 
   ```bash
   pip install build twine
   ```

## Étape 1 : Préparer le Package

### 1.1 Vérifier la version

Dans `pyproject.toml`, vérifiez/mettez à jour la version :
```toml
[project]
name = "pypaginator"
version = "0.1.0"  # ← Mettre à jour ici
```

### 1.2 Mettre à jour CHANGELOG.md

```markdown
## [0.1.0] - 2025-12-22

### Added
- Initial release
- Core pagination functionality
- SQLAlchemy support
- Filtering and search
- FastAPI integration
```

### 1.3 Vérifier la qualité

```bash
# Tests
pytest

# Type checking
mypy src/pypaginator

# Linting
ruff check src/pypaginator

# Formatting
black --check src/pypaginator tests
```

Ou utilisez :
```bash
make quality
```

## Étape 2 : Construire le Package

```bash
# Nettoyer les builds précédents
rm -rf dist/ build/ *.egg-info

# Construire
python -m build
```

Cela créera :
- `dist/pypaginator-0.1.0-py3-none-any.whl` (wheel)
- `dist/pypaginator-0.1.0.tar.gz` (source distribution)

## Étape 3 : Vérifier le Package

```bash
# Vérifier la distribution
twine check dist/*
```

Sortie attendue :
```
Checking dist/pypaginator-0.1.0-py3-none-any.whl: PASSED
Checking dist/pypaginator-0.1.0.tar.gz: PASSED
```

## Étape 4 : Tester Localement

```bash
# Créer un environnement de test
python -m venv test_venv
test_venv\Scripts\activate  # Windows
# ou : source test_venv/bin/activate  # Linux/Mac

# Installer depuis le wheel local
pip install dist/pypaginator-0.1.0-py3-none-any.whl

# Tester
python -c "from pypaginator import PageParams; print('OK')"

# Désactiver
deactivate
```

## Étape 5 : Publier sur Test PyPI (Recommandé)

### 5.1 Configurer les credentials

Créez `~/.pypirc` :
```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgE...  # Votre token Test PyPI

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgE...  # Votre token PyPI
```

### 5.2 Publier sur Test PyPI

```bash
twine upload --repository testpypi dist/*
```

### 5.3 Tester l'installation depuis Test PyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pypaginator
```

Note : `--extra-index-url` permet d'installer les dépendances depuis PyPI normal.

## Étape 6 : Publier sur PyPI Production

### 6.1 Vérifications finales

- [ ] Version correcte dans `pyproject.toml`
- [ ] CHANGELOG.md à jour
- [ ] README.md complet et clair
- [ ] Tous les tests passent
- [ ] Package testé sur Test PyPI
- [ ] Git tag créé

### 6.2 Créer un Git tag

```bash
git tag v0.1.0
git push origin v0.1.0
```

### 6.3 Publier

```bash
twine upload dist/*
```

### 6.4 Vérifier sur PyPI

Visitez : https://pypi.org/project/pypaginator/

## Étape 7 : Publier via GitHub Actions (Recommandé)

### 7.1 Configurer les secrets GitHub

1. Allez sur https://pypi.org/manage/account/token/
2. Créez un API token avec scope "Entire account" ou "Project: pypaginator"
3. Dans GitHub : Settings → Secrets → Actions → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-AgE...` (votre token)

### 7.2 Créer une release GitHub

1. Créez et poussez un tag :
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

2. Allez sur GitHub : Releases → Draft a new release
   - Tag: `v0.1.0`
   - Title: `PyPaginator v0.1.0`
   - Description: Copiez depuis CHANGELOG.md
   - Publish release

3. Le workflow `.github/workflows/publish.yml` se déclenchera automatiquement et publiera sur PyPI

## Étape 8 : Post-Publication

### 8.1 Vérifier l'installation

```bash
pip install pypaginator
python -c "from pypaginator import PageParams; print('✓ Installed successfully')"
```

### 8.2 Annoncer la release

- **Twitter/X** : Tweet avec #Python #OpenSource
- **Reddit** : r/Python
- **Dev.to** : Article de blog
- **GitHub Discussions** : Annonce

### 8.3 Monitorer

- **PyPI Stats** : https://pypistats.org/packages/pypaginator
- **GitHub Issues** : Répondre aux questions
- **Documentation** : Améliorer selon les retours

## Versions Suivantes

### Patch Release (0.1.1)

Pour des bug fixes :
```bash
# 1. Mettre à jour version dans pyproject.toml
# 2. Mettre à jour CHANGELOG.md
# 3. Commit et tag
git commit -am "Bump version to 0.1.1"
git tag v0.1.1
git push origin v0.1.1
# 4. Créer release GitHub (déclenche publication automatique)
```

### Minor Release (0.2.0)

Pour de nouvelles fonctionnalités :
- Mettez à jour la documentation
- Ajoutez des exemples
- Annoncez les nouveautés

### Major Release (1.0.0)

Pour des breaking changes :
- Documentation de migration
- Annonce préalable
- Support de l'ancienne version

## Troubleshooting

### Erreur : "File already exists"

Le package existe déjà sur PyPI avec cette version. Vous devez :
1. Incrémenter la version dans `pyproject.toml`
2. Reconstruire : `python -m build`
3. Republier

### Erreur : "Invalid credentials"

Vérifiez votre token PyPI dans `~/.pypirc` ou utilisez :
```bash
twine upload --username __token__ --password pypi-AgE... dist/*
```

### Erreur : "Package name already taken"

Le nom "pypaginator" est déjà pris. Choisissez un autre nom :
- `py-paginator`
- `pagination-toolkit`
- `advanced-paginator`
- etc.

Mettez à jour `pyproject.toml` :
```toml
[project]
name = "py-paginator"  # Nouveau nom
```

## Ressources

- **PyPI Guide** : https://packaging.python.org/tutorials/packaging-projects/
- **Twine Docs** : https://twine.readthedocs.io/
- **Semantic Versioning** : https://semver.org/
- **CHANGELOG Format** : https://keepachangelog.com/

## Checklist Finale

- [ ] Version mise à jour dans `pyproject.toml`
- [ ] CHANGELOG.md à jour
- [ ] README.md vérifié
- [ ] Tests passent (`pytest`)
- [ ] Qualité OK (`make quality`)
- [ ] Package construit (`python -m build`)
- [ ] Package vérifié (`twine check dist/*`)
- [ ] Testé localement
- [ ] Testé sur Test PyPI (optionnel)
- [ ] Git tag créé et poussé
- [ ] Publié sur PyPI
- [ ] Installation vérifiée
- [ ] Release GitHub créée
- [ ] Annoncé publiquement

---

**Félicitations !** Votre package est maintenant publié sur PyPI ! 🎉

