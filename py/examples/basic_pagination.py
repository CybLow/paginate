"""Basic Pagination Example.

This example demonstrates simple offset-based pagination
with in-memory data using pypaginate.
"""

from pypaginate import PageParams
from pypaginate.engines import MemoryPaginator


def main() -> None:
    """Demonstrate basic pagination with in-memory data."""
    # Sample data
    users = [
        {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
        for i in range(1, 101)  # 100 users
    ]

    # Create paginator
    paginator = MemoryPaginator()

    # Page 1 with 10 items per page
    params = PageParams(page=1, limit=10)
    result = paginator.paginate(users, params)
    page = result.to_page()

    print("=== Page 1 ===")
    print(f"Items: {len(page.items)}")
    print(f"Total: {page.total}")
    print(f"Page: {page.page}/{(page.total + page.limit - 1) // page.limit}")
    print(f"First item: {page.items[0]}")
    print(f"Last item: {page.items[-1]}")

    # Page 5
    params = PageParams(page=5, limit=10)
    result = paginator.paginate(users, params)
    page = result.to_page()

    print("\n=== Page 5 ===")
    print(f"Items: {len(page.items)}")
    print(f"First item: {page.items[0]}")
    print(f"Last item: {page.items[-1]}")


if __name__ == "__main__":
    main()
