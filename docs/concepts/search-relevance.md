# Search & Relevance

pypaginate provides text search capabilities with relevance scoring and fuzzy matching.
This page explains how search works and how relevance is calculated.

## Search Overview

```{mermaid}
graph LR
    subgraph "Search Pipeline"
        Q[Query] --> T[Tokenizer]
        T --> N[Normalizer]
        N --> M[Matcher]
        M --> S[Scorer]
        S --> R[Ranked Results]
    end
```

Search involves several stages:

1. **Tokenize** - Break query into searchable terms
2. **Normalize** - Lowercase, remove accents, stem words
3. **Match** - Find documents containing terms
4. **Score** - Calculate relevance for each match
5. **Rank** - Sort by relevance score

## Search Types

### Exact Search

Finds documents containing the exact query string:

```python
results = await search(query, search="john doe")
# Matches: "John Doe", "john doe", "JOHN DOE"
# No match: "John A. Doe", "Johnny Doe"
```

### Partial Search

Finds documents containing any part of the query:

```python
results = await search(query, search="john", partial=True)
# Matches: "John", "Johnny", "Johnson"
```

### Fuzzy Search

Finds approximate matches, tolerating typos:

```python
results = await search(query, search="jonh", fuzzy=True)
# Matches: "John" (typo corrected)
# Matches: "Jon" (close enough)
```

## Relevance Scoring

### Scoring Factors

```{mermaid}
graph TB
    subgraph "Relevance Score Components"
        TF[Term Frequency<br/>How often term appears]
        IDF[Inverse Doc Frequency<br/>How rare term is]
        FL[Field Length<br/>Shorter = more relevant]
        FW[Field Weight<br/>Title > Description]
        FP[Field Position<br/>Earlier = more relevant]
    end
    
    TF --> Score
    IDF --> Score
    FL --> Score
    FW --> Score
    FP --> Score
    Score[Final Score]
```

### TF-IDF Scoring

The classic TF-IDF (Term Frequency-Inverse Document Frequency) formula:

```
score = TF(term, document) × IDF(term, corpus)

Where:
  TF = count(term in doc) / total_terms_in_doc
  IDF = log(total_docs / docs_containing_term)
```

Terms that appear frequently in a document but rarely across all documents
score highest.

### Example Scoring

| Document | Query: "python" | TF | IDF | Score |
|----------|----------------|-----|-----|-------|
| "Python programming in Python" | 2 occurrences | 0.5 | 2.0 | 1.0 |
| "Learn Python basics" | 1 occurrence | 0.33 | 2.0 | 0.66 |
| "Java and JavaScript guide" | 0 occurrences | 0 | - | 0 |

## Multi-Field Search

When searching across multiple fields, weights determine relative importance:

```{mermaid}
graph LR
    subgraph "Field Weights"
        T["Title (weight: 3.0)"] --> S[Combined Score]
        D["Description (weight: 1.0)"] --> S
        C["Content (weight: 0.5)"] --> S
    end
```

### Configuration

```python
from pypaginate import SearchOptions

options = SearchOptions(
    fields={
        "title": 3.0,        # Most important
        "description": 1.0,  # Normal weight
        "tags": 2.0,         # Important
        "content": 0.5       # Less important
    }
)

results = await search(query, search="python", options=options)
```

### Score Combination

Final score combines per-field scores:

```
total_score = sum(field_score × field_weight) / sum(field_weights)
```

## Fuzzy Matching

### Levenshtein Distance

Fuzzy matching uses Levenshtein distance - the minimum number of single-character
edits (insertions, deletions, substitutions) to transform one string into another:

```{mermaid}
graph LR
    subgraph "Levenshtein Distance Examples"
        E1["'cat' → 'hat' = 1"]
        E2["'book' → 'back' = 2"]
        E3["'python' → 'pythn' = 1"]
    end
```

| From | To | Distance | Edits |
|------|----|----------|-------|
| cat | hat | 1 | substitute c→h |
| book | back | 2 | substitute o→a, o→c |
| python | pythn | 1 | delete o |
| hello | helo | 1 | delete l |

### Similarity Threshold

A threshold determines how fuzzy the match can be:

```python
from pypaginate import FuzzyOptions

options = FuzzyOptions(
    threshold=0.7,  # 70% similarity required
    max_distance=2  # Maximum 2 edits
)
```

```{mermaid}
graph TB
    subgraph "Threshold Examples (0.7)"
        M1["'john' vs 'jon'<br/>Similarity: 0.86 ✓"]
        M2["'john' vs 'joan'<br/>Similarity: 0.75 ✓"]
        M3["'john' vs 'jack'<br/>Similarity: 0.50 ✗"]
    end
```

### Fuzzy Algorithm

```{mermaid}
flowchart TD
    Q[Query: 'jonh'] --> T[Tokenize]
    T --> C{Candidates}
    C --> W1[john - dist 1]
    C --> W2[jon - dist 1]
    C --> W3[jonas - dist 2]
    W1 --> F{Above threshold?}
    W2 --> F
    W3 --> F
    F -->|Yes| R[Include in results]
    F -->|No| X[Exclude]
```

## SQL Search Implementation

### PostgreSQL Full-Text Search

For PostgreSQL, pypaginate can use built-in full-text search:

```sql
-- Creates tsvector for searching
SELECT *, ts_rank(to_tsvector(title), plainto_tsquery('python')) as rank
FROM articles
WHERE to_tsvector(title) @@ plainto_tsquery('python')
ORDER BY rank DESC;
```

### LIKE-Based Fallback

For databases without full-text search:

```sql
SELECT *
FROM articles
WHERE LOWER(title) LIKE '%python%'
   OR LOWER(description) LIKE '%python%';
```

### Trigram Similarity (PostgreSQL)

For fuzzy matching in PostgreSQL using pg_trgm:

```sql
-- Find similar names
SELECT *, similarity(name, 'jonh') as sim
FROM users
WHERE similarity(name, 'jonh') > 0.3
ORDER BY sim DESC;
```

## In-Memory Search

For in-memory data sources, search uses Python implementations:

```{mermaid}
flowchart LR
    subgraph "In-Memory Search"
        D[Data] --> I[Build Index]
        I --> Q[Query]
        Q --> M[Match]
        M --> S[Score]
        S --> R[Results]
    end
```

### Indexing Strategy

```python
# Simple inverted index
index = defaultdict(set)
for doc_id, doc in enumerate(documents):
    for word in tokenize(doc.text):
        index[normalize(word)].add(doc_id)

# Search
def search(query):
    terms = [normalize(t) for t in tokenize(query)]
    matching_docs = set.intersection(*[index[t] for t in terms])
    return matching_docs
```

## Search Options

### Full Configuration

```python
from pypaginate import SearchOptions, FuzzyOptions

options = SearchOptions(
    # Fields to search with weights
    fields={
        "title": 3.0,
        "description": 1.0,
        "content": 0.5
    },
    
    # Matching options
    mode="any",  # "all" requires all terms, "any" requires at least one
    
    # Fuzzy matching
    fuzzy=FuzzyOptions(
        enabled=True,
        threshold=0.7,
        max_distance=2
    ),
    
    # Highlighting
    highlight=True,
    highlight_tag="<mark>",
    
    # Minimum score threshold
    min_score=0.1
)
```

### Search Modes

| Mode | Description | Example |
|------|-------------|---------|
| `all` | All terms must match | "python web" → both required |
| `any` | Any term can match | "python web" → either sufficient |
| `phrase` | Exact phrase match | "python web" → must be adjacent |

## Result Highlighting

Search results can include highlighted matches:

```python
results = await search(query, search="python", highlight=True)

for item in results.items:
    print(item.highlights)
    # {"title": "Learn <mark>Python</mark> basics"}
```

### Highlight Configuration

```python
options = SearchOptions(
    highlight=True,
    highlight_tag="<em>",           # HTML tag to use
    highlight_max_length=200,       # Truncate long fields
    highlight_fragment_size=50,     # Context around match
    highlight_number_of_fragments=3 # Max fragments per field
)
```

## Performance Optimization

### Indexing

For best search performance, create appropriate indexes:

```sql
-- PostgreSQL full-text index
CREATE INDEX idx_articles_search 
ON articles USING GIN (to_tsvector('english', title || ' ' || description));

-- PostgreSQL trigram index for fuzzy
CREATE INDEX idx_users_name_trgm 
ON users USING GIN (name gin_trgm_ops);
```

### Query Optimization

| Tip | Description |
|-----|-------------|
| Limit search fields | Search fewer fields = faster queries |
| Use appropriate thresholds | Lower fuzzy threshold = faster matching |
| Index searched columns | Full-text or trigram indexes |
| Paginate results | Don't load all matches at once |

### Caching

For frequently searched terms:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query_hash, search_term):
    return perform_search(search_term)
```

## Search Quality

### Improving Relevance

| Technique | Description |
|-----------|-------------|
| **Stop words** | Ignore common words ("the", "a", "is") |
| **Stemming** | Match word roots ("running" → "run") |
| **Synonyms** | Match related terms ("car" → "automobile") |
| **Boosting** | Increase weight for important fields |

### Measuring Quality

| Metric | Description |
|--------|-------------|
| **Precision** | % of returned results that are relevant |
| **Recall** | % of relevant results that are returned |
| **MRR** | Mean Reciprocal Rank - how high relevant results appear |

## Further Reading

- [User Guide: Text Search](../search/text-search.md) - Basic usage
- [User Guide: Fuzzy Matching](../search/fuzzy.md) - Fuzzy search
- [Filter Expressions](filter-expressions.md) - Combine search with filters
- [Architecture](architecture.md) - Overall library design
