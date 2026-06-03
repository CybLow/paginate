"""Filtering Example.

This example demonstrates how to use JSON Logic filtering
with pypaginate's FilterEngine.
"""

from pypaginate.filters.predicates import FilterEngine


def main() -> None:
    """Demonstrate filtering with various operators."""
    engine = FilterEngine()

    # Sample data
    users = [
        {"name": "Alice", "age": 30, "status": "active", "role": "admin"},
        {"name": "Bob", "age": 25, "status": "inactive", "role": "user"},
        {"name": "Charlie", "age": 35, "status": "active", "role": "user"},
        {"name": "Diana", "age": 28, "status": "active", "role": "moderator"},
        {"name": "Eve", "age": 22, "status": "inactive", "role": "user"},
    ]

    # Simple equality filter
    print("=== Active Users ===")
    active_users = engine.filter(users, {"status": {"eq": "active"}})
    for user in active_users:
        print(f"  {user['name']} ({user['age']})")

    # Greater than or equal filter
    print("\n=== Users 28 or older ===")
    older_users = engine.filter(users, {"age": {"gte": 28}})
    for user in older_users:
        print(f"  {user['name']} ({user['age']})")

    # IN operator
    print("\n=== Admins or Moderators ===")
    staff = engine.filter(users, {"role": {"in": ["admin", "moderator"]}})
    for user in staff:
        print(f"  {user['name']} ({user['role']})")

    # Complex AND filter
    print("\n=== Active Users over 25 ===")
    complex_filter = {
        "and": [
            {"status": {"eq": "active"}},
            {"age": {"gt": 25}},
        ]
    }
    filtered = engine.filter(users, complex_filter)
    for user in filtered:
        print(f"  {user['name']} ({user['age']}, {user['status']})")

    # OR filter
    print("\n=== Young (under 25) OR Inactive ===")
    or_filter = {
        "or": [
            {"age": {"lt": 25}},
            {"status": {"eq": "inactive"}},
        ]
    }
    filtered = engine.filter(users, or_filter)
    for user in filtered:
        print(f"  {user['name']} ({user['age']}, {user['status']})")


if __name__ == "__main__":
    main()
