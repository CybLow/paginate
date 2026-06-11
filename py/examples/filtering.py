"""Filtering example.

``filter()`` keeps the items matching a ``FilterSpec`` (or a flat list of them,
or a nested ``And()`` / ``Or()`` group), in their original order. Operators are
plain strings defined once in the Rust core.

Run:
    uv run python examples/filtering.py
"""

from pypaginate import And, FilterSpec, Or, filter  # noqa: A004 (public API name)


def main() -> None:
    """Demonstrate filtering with various operators and boolean groups."""
    users = [
        {"name": "Alice", "age": 30, "status": "active", "role": "admin"},
        {"name": "Bob", "age": 25, "status": "inactive", "role": "user"},
        {"name": "Charlie", "age": 35, "status": "active", "role": "user"},
        {"name": "Diana", "age": 28, "status": "active", "role": "moderator"},
        {"name": "Eve", "age": 22, "status": "inactive", "role": "user"},
    ]

    # Simple equality.
    print("=== Active users ===")
    for user in filter(users, FilterSpec(field="status", operator="eq", value="active")):
        print(f"  {user['name']} ({user['age']})")

    # Greater than or equal.
    print("\n=== Users 28 or older ===")
    for user in filter(users, FilterSpec(field="age", operator="gte", value=28)):
        print(f"  {user['name']} ({user['age']})")

    # Membership.
    print("\n=== Admins or moderators ===")
    staff = filter(users, FilterSpec(field="role", operator="in", value=["admin", "moderator"]))
    for user in staff:
        print(f"  {user['name']} ({user['role']})")

    # AND group: active AND over 25.
    print("\n=== Active users over 25 ===")
    active_over_25 = filter(
        users,
        And(
            FilterSpec(field="status", operator="eq", value="active"),
            FilterSpec(field="age", operator="gt", value=25),
        ),
    )
    for user in active_over_25:
        print(f"  {user['name']} ({user['age']}, {user['status']})")

    # OR group: young (under 25) OR inactive.
    print("\n=== Young (under 25) OR inactive ===")
    young_or_inactive = filter(
        users,
        Or(
            FilterSpec(field="age", operator="lt", value=25),
            FilterSpec(field="status", operator="eq", value="inactive"),
        ),
    )
    for user in young_or_inactive:
        print(f"  {user['name']} ({user['age']}, {user['status']})")


if __name__ == "__main__":
    main()
