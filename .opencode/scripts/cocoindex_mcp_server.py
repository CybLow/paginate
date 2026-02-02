#!/usr/bin/env python3
"""CocoIndex MCP Server wrapper.

This script wraps CocoIndex as an MCP server for OpenCode integration.
It provides semantic code search capabilities via MCP protocol.

Usage:
    python cocoindex_mcp_server.py

Requires:
    - cocoindex
    - mcp (pip install mcp)
    - PostgreSQL with pgvector
    - sentence-transformers
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

# Check if mcp is available
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool


# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize MCP server
server = Server("cocoindex-pypaginate")

# Correct table names (flow_name__export_name format, all lowercase)
CODE_TABLE = "pypaginatecodesearch__code_embeddings"
DOCS_TABLE = "pypaginatedocssearch__docs_embeddings"


def get_db_connection() -> Any:
    """Get database connection for queries."""
    import psycopg2

    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    return psycopg2.connect(db_url)


def embed_query(query: str) -> list[float]:
    """Generate embedding for a query using SentenceTransformer.

    Uses the same model as the indexing flow for consistency.
    """
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embedding = model.encode(query, convert_to_numpy=True)
    return embedding.tolist()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_code",
            description="Search pypaginate source code semantically. Use this to find relevant code snippets, functions, or classes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query to search for in the codebase",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="search_docs",
            description="Search pypaginate documentation semantically. Use this to find relevant documentation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query to search for in documentation",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="index_status",
            description="Get the status of the CocoIndex semantic search index.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "search_code":
        return await _search_code(arguments)
    elif name == "search_docs":
        return await _search_docs(arguments)
    elif name == "index_status":
        return await _index_status()
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _search_code(arguments: dict[str, Any]) -> list[TextContent]:
    """Search code using vector similarity."""
    query = arguments.get("query", "")
    top_k = arguments.get("top_k", 5)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if table exists
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """,
            (CODE_TABLE,),
        )
        exists = cur.fetchone()[0]

        if not exists:
            conn.close()
            return [
                TextContent(
                    type="text",
                    text="Code index not yet created. Run: cocoindex update .opencode/scripts/cocoindex_flow.py",
                )
            ]

        # Generate query embedding
        query_embedding = embed_query(query)

        # Vector similarity search using pgvector cosine distance
        cur.execute(
            f"""
            SELECT filename, location, code, 1 - (embedding <=> %s::vector) as similarity
            FROM {CODE_TABLE}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """,  # noqa: S608 - table name is a trusted constant
            (query_embedding, query_embedding, top_k),
        )

        results = cur.fetchall()
        conn.close()

        if not results:
            return [TextContent(type="text", text=f"No results found for: {query}")]

        formatted = [f"## Code Search Results for: {query}\n"]
        for filename, location, code, similarity in results:
            formatted.append(f"### {filename} (similarity: {similarity:.3f})")
            formatted.append(f"Location: {location}")
            formatted.append(f"```python\n{code}\n```\n")

        return [TextContent(type="text", text="\n".join(formatted))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error searching code: {e}")]


async def _search_docs(arguments: dict[str, Any]) -> list[TextContent]:
    """Search documentation using vector similarity."""
    query = arguments.get("query", "")
    top_k = arguments.get("top_k", 5)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if table exists
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """,
            (DOCS_TABLE,),
        )
        exists = cur.fetchone()[0]

        if not exists:
            conn.close()
            return [
                TextContent(
                    type="text",
                    text="Docs index not yet created. Run: cocoindex update .opencode/scripts/cocoindex_flow.py",
                )
            ]

        # Generate query embedding
        query_embedding = embed_query(query)

        # Vector similarity search using pgvector cosine distance
        cur.execute(
            f"""
            SELECT filename, location, content, 1 - (embedding <=> %s::vector) as similarity
            FROM {DOCS_TABLE}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """,  # noqa: S608 - table name is a trusted constant
            (query_embedding, query_embedding, top_k),
        )

        results = cur.fetchall()
        conn.close()

        if not results:
            return [TextContent(type="text", text=f"No results found for: {query}")]

        formatted = [f"## Documentation Search Results for: {query}\n"]
        for filename, location, content, similarity in results:
            formatted.append(f"### {filename} (similarity: {similarity:.3f})")
            formatted.append(f"Location: {location}")
            formatted.append(f"{content}\n")

        return [TextContent(type="text", text="\n".join(formatted))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error searching docs: {e}")]


async def _index_status() -> list[TextContent]:
    """Get index status."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        status = {"code_index": False, "docs_index": False, "code_count": 0, "docs_count": 0}

        # Check code index
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """,
            (CODE_TABLE,),
        )
        status["code_index"] = cur.fetchone()[0]

        if status["code_index"]:
            cur.execute(f"SELECT COUNT(*) FROM {CODE_TABLE}")  # noqa: S608
            status["code_count"] = cur.fetchone()[0]

        # Check docs index
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """,
            (DOCS_TABLE,),
        )
        status["docs_index"] = cur.fetchone()[0]

        if status["docs_index"]:
            cur.execute(f"SELECT COUNT(*) FROM {DOCS_TABLE}")  # noqa: S608
            status["docs_count"] = cur.fetchone()[0]

        conn.close()

        return [TextContent(type="text", text=json.dumps(status, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error getting status: {e}")]


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
