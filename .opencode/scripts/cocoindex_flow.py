"""CocoIndex flow for pypaginate codebase semantic search.

This script indexes the pypaginate codebase for semantic search using Tree-sitter
for intelligent code chunking.

Usage:
    # Update the index
    cocoindex update .opencode/scripts/cocoindex_flow.py

    # Start the server (for CocoInsight or MCP integration)
    cocoindex server .opencode/scripts/cocoindex_flow.py -a 127.0.0.1:8090

    # Run queries interactively
    python .opencode/scripts/cocoindex_flow.py

Environment variables:
    GOOGLE_API_KEY: Google API key (for Gemini embeddings)
    COCOINDEX_DATABASE_URL: PostgreSQL connection string (required)
"""

# NOTE: Do NOT use `from __future__ import annotations` - it breaks cocoindex type detection

import functools
import os

import cocoindex
import numpy as np
from cocoindex import functions, sources, targets
from numpy.typing import NDArray


# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@cocoindex.transform_flow()
def code_to_embedding(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[NDArray[np.float32]]:
    """Embed text using SentenceTransformer (local, no API calls).

    Using transform_flow to share embedding logic between indexing and query.
    """
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(model="sentence-transformers/all-MiniLM-L6-v2")
    )


@cocoindex.flow_def(name="PypaginateCodeSearch")
def code_search_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """Index pypaginate codebase for semantic code search.

    Uses Tree-sitter for intelligent Python code chunking.
    """
    # Source: Python files from src directory
    data_scope["files"] = flow_builder.add_source(
        sources.LocalFile(
            path=os.path.join(PROJECT_ROOT, "src"),
            included_patterns=["**/*.py"],
            excluded_patterns=["**/__pycache__/**", "**/*.pyc"],
        )
    )

    # Collector for code embeddings
    code_embeddings = data_scope.add_collector()

    # Process each Python file
    with data_scope["files"].row() as file:
        # Detect programming language for Tree-sitter
        file["language"] = file["filename"].transform(functions.DetectProgrammingLanguage())

        # Split into semantic chunks using Tree-sitter
        file["chunks"] = file["content"].transform(
            functions.SplitRecursively(),
            language=file["language"],
            chunk_size=1000,
            min_chunk_size=200,
            chunk_overlap=200,
        )

        # Process each chunk
        with file["chunks"].row() as chunk:
            # Generate embedding using shared transform_flow
            chunk["embedding"] = chunk["text"].call(code_to_embedding)

            # Collect for export
            code_embeddings.collect(
                filename=file["filename"],
                location=chunk["location"],
                code=chunk["text"],
                embedding=chunk["embedding"],
                start=chunk["start"],
                end=chunk["end"],
            )

    # Export to PostgreSQL with vector index
    code_embeddings.export(
        "code_embeddings",
        targets.Postgres(),
        primary_key_fields=["filename", "location"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
            )
        ],
    )


@cocoindex.flow_def(name="PypaginateDocsSearch")
def docs_search_flow(
    flow_builder: cocoindex.FlowBuilder,
    data_scope: cocoindex.DataScope,
) -> None:
    """Index pypaginate documentation for semantic search.

    Uses Tree-sitter for intelligent Markdown chunking.
    """
    # Source: Markdown files from docs directory
    data_scope["files"] = flow_builder.add_source(
        sources.LocalFile(
            path=os.path.join(PROJECT_ROOT, "docs"),
            included_patterns=["**/*.md"],
            excluded_patterns=["**/node_modules/**"],
        )
    )

    # Collector for doc embeddings
    doc_embeddings = data_scope.add_collector()

    # Process each doc file
    with data_scope["files"].row() as file:
        # Detect language for Tree-sitter
        file["language"] = file["filename"].transform(functions.DetectProgrammingLanguage())

        # Split into chunks using Tree-sitter
        file["chunks"] = file["content"].transform(
            functions.SplitRecursively(),
            language=file["language"],
            chunk_size=1500,
            min_chunk_size=300,
            chunk_overlap=300,
        )

        # Process each chunk
        with file["chunks"].row() as chunk:
            # Generate embedding using shared transform_flow
            chunk["embedding"] = chunk["text"].call(code_to_embedding)

            # Collect for export
            doc_embeddings.collect(
                filename=file["filename"],
                location=chunk["location"],
                content=chunk["text"],
                embedding=chunk["embedding"],
                start=chunk["start"],
                end=chunk["end"],
            )

    # Export to PostgreSQL with vector index
    doc_embeddings.export(
        "docs_embeddings",
        targets.Postgres(),
        primary_key_fields=["filename", "location"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
            )
        ],
    )


@functools.cache
def connection_pool():
    """Get a connection pool to the database."""
    from psycopg_pool import ConnectionPool

    return ConnectionPool(os.environ["COCOINDEX_DATABASE_URL"])


# Query handler for code search
@code_search_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(embedding=["embedding"], score="score")
)
def search_code(query: str) -> cocoindex.QueryOutput:
    """Search code embeddings with a query."""
    from pgvector.psycopg import register_vector

    table_name = cocoindex.utils.get_target_default_name(code_search_flow, "code_embeddings")
    query_vector = code_to_embedding.eval(query)

    with connection_pool().connection() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT filename, code, embedding, embedding <=> %s AS distance, start, "end"
                FROM {table_name} ORDER BY distance LIMIT %s
            """,  # noqa: S608 - table name from trusted cocoindex utility
                (query_vector, 10),
            )
            return cocoindex.QueryOutput(
                query_info=cocoindex.QueryInfo(
                    embedding=query_vector,
                    similarity_metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
                ),
                results=[
                    {
                        "filename": row[0],
                        "code": row[1],
                        "embedding": row[2],
                        "score": 1.0 - row[3],
                        "start": row[4],
                        "end": row[5],
                    }
                    for row in cur.fetchall()
                ],
            )


# Query handler for docs search
@docs_search_flow.query_handler(
    result_fields=cocoindex.QueryHandlerResultFields(embedding=["embedding"], score="score")
)
def search_docs(query: str) -> cocoindex.QueryOutput:
    """Search docs embeddings with a query."""
    from pgvector.psycopg import register_vector

    table_name = cocoindex.utils.get_target_default_name(docs_search_flow, "docs_embeddings")
    query_vector = code_to_embedding.eval(query)

    with connection_pool().connection() as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT filename, content, embedding, embedding <=> %s AS distance, start, "end"
                FROM {table_name} ORDER BY distance LIMIT %s
            """,  # noqa: S608 - table name from trusted cocoindex utility
                (query_vector, 10),
            )
            return cocoindex.QueryOutput(
                query_info=cocoindex.QueryInfo(
                    embedding=query_vector,
                    similarity_metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
                ),
                results=[
                    {
                        "filename": row[0],
                        "content": row[1],
                        "embedding": row[2],
                        "score": 1.0 - row[3],
                        "start": row[4],
                        "end": row[5],
                    }
                    for row in cur.fetchall()
                ],
            )


def main() -> None:
    """Interactive query interface."""
    # Update indexes
    print("Updating code index...")
    code_stats = code_search_flow.update()
    print(f"Code index updated: {code_stats}")

    print("Updating docs index...")
    docs_stats = docs_search_flow.update()
    print(f"Docs index updated: {docs_stats}")

    print("\n" + "=" * 60)
    print("pypaginate Semantic Search")
    print("=" * 60)
    print("\nCommands:")
    print("  code <query>  - Search code")
    print("  docs <query>  - Search documentation")
    print("  quit          - Exit")
    print()

    while True:
        try:
            user_input = input("Search> ").strip()
            if not user_input or user_input == "quit":
                break

            if user_input.startswith("code "):
                query = user_input[5:].strip()
                output = search_code(query)
                print(f"\nCode results for '{query}':")
                for r in output.results:
                    start = r.get("start", {})
                    end = r.get("end", {})
                    line_info = f"L{start.get('line', '?')}-L{end.get('line', '?')}"
                    print(f"  [{r['score']:.3f}] {r['filename']} ({line_info})")
                    preview = r["code"][:100].replace("\n", " ")
                    print(f"          {preview}...")
                print()

            elif user_input.startswith("docs "):
                query = user_input[5:].strip()
                output = search_docs(query)
                print(f"\nDocs results for '{query}':")
                for r in output.results:
                    print(f"  [{r['score']:.3f}] {r['filename']}")
                    preview = r["content"][:100].replace("\n", " ")
                    print(f"          {preview}...")
                print()

            else:
                print("Unknown command. Use 'code <query>' or 'docs <query>'")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    cocoindex.init()
    main()
