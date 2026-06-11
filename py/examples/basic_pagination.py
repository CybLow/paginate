"""Basic pagination example.

Offset-based pagination over an in-memory list with ``paginate()``. The native
core does the slicing and derives the page metadata; your objects are returned
untouched.

Run:
    uv run python examples/basic_pagination.py
"""

from pypaginate import OffsetParams, paginate


def main() -> None:
    """Demonstrate basic offset pagination with in-memory data."""
    users = [
        {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
        for i in range(1, 101)  # 100 users
    ]

    # Page 1, 10 items per page.
    page = paginate(users, OffsetParams(page=1, limit=10))

    print("=== Page 1 ===")
    print(f"Items: {len(page)}")  # OffsetPage is sized, iterable, and indexable
    print(f"Total: {page.total}")
    print(f"Page:  {page.page}/{page.pages}")
    print(f"Has next: {page.has_next}")
    print(f"First item: {page[0]}")
    print(f"Last item:  {page[-1]}")

    # Page 5.
    page = paginate(users, OffsetParams(page=5, limit=10))

    print("\n=== Page 5 ===")
    print(f"Items: {len(page)}")
    print(f"Has previous: {page.has_previous}")
    print(f"First item: {page[0]}")
    print(f"Last item:  {page[-1]}")

    # A page past the end is not an error: empty items, metadata preserved.
    page = paginate(users, OffsetParams(page=999, limit=10))

    print("\n=== Page 999 (out of range) ===")
    print(f"Items: {len(page)}")  # 0
    print(f"Total still: {page.total}, pages still: {page.pages}")


if __name__ == "__main__":
    main()
