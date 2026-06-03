"""Keyset (Cursor) Pagination Example.

This example demonstrates cursor-based pagination which is more
efficient for large datasets compared to offset-based pagination.

Keyset pagination uses a cursor (typically based on the last item's
sort key) to fetch the next page, avoiding the performance issues
of OFFSET for deep pages.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from pypaginate.core import KeysetPageParams


def generate_sample_data(count: int = 100) -> list[dict[str, Any]]:
    """Generate sample data with timestamps."""
    base_time = datetime.now(tz=UTC)
    return [
        {
            "id": i,
            "title": f"Article {i}",
            "created_at": (base_time - timedelta(hours=i)).isoformat(),
            "views": (count - i) * 10,
        }
        for i in range(1, count + 1)
    ]


def simulate_keyset_pagination(
    data: list[dict[str, Any]],
    cursor: str | None,
    limit: int,
    sort_key: str = "id",
) -> tuple[list[dict[str, Any]], str | None]:
    """Simulate keyset pagination on in-memory data.

    In production, this would be done at the database level using
    WHERE id > cursor_value ORDER BY id LIMIT n.
    """
    if cursor is None:
        # First page
        items = data[:limit]
    else:
        # Find starting point
        cursor_value = int(cursor)
        start_idx = next(
            (i for i, item in enumerate(data) if item[sort_key] > cursor_value),
            len(data),
        )
        items = data[start_idx : start_idx + limit]

    # Generate next cursor
    next_cursor = str(items[-1][sort_key]) if len(items) == limit else None

    return items, next_cursor


def main() -> None:
    """Demonstrate keyset pagination."""
    data = generate_sample_data(50)
    limit = 10

    print("=== Keyset Pagination Demo ===\n")

    # Create keyset params
    params = KeysetPageParams(limit=limit, cursor=None)
    print(f"Initial params: limit={params.limit}, cursor={params.cursor}")

    # Fetch pages
    cursor: str | None = None
    page_num = 1

    while True:
        items, next_cursor = simulate_keyset_pagination(data, cursor=cursor, limit=limit)

        print(f"\n--- Page {page_num} ---")
        print(f"Cursor used: {cursor or 'None (first page)'}")
        print(f"Items: {len(items)}")
        print(f"First: id={items[0]['id']}, title={items[0]['title']}")
        print(f"Last: id={items[-1]['id']}, title={items[-1]['title']}")
        print(f"Next cursor: {next_cursor}")

        if next_cursor is None:
            print("\n✓ No more pages")
            break

        cursor = next_cursor
        page_num += 1

        # Safety limit for demo
        if page_num > 10:
            print("\n(Stopping demo after 10 pages)")
            break


if __name__ == "__main__":
    main()
