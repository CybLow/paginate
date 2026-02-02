---
description: Run or create end-to-end tests with Playwright browser automation
agent: e2e-tester
---

# /e2e

Run or create end-to-end tests using Playwright.

## Usage

```
/e2e [action] [target]
```

## Actions

### Run Tests

```
/e2e run                    # Run all E2E tests
/e2e run tests/e2e/login    # Run specific test file
/e2e run --headed           # Run with visible browser
```

### Create Tests

```
/e2e create login flow      # Create tests for login flow
/e2e create user dashboard  # Create tests for dashboard
```

### Debug

```
/e2e debug test_login       # Debug specific failing test
/e2e codegen                # Open Playwright codegen
```

## Examples

```
/e2e run
/e2e create tests for the pagination component
/e2e debug the failing checkout test
/e2e run with screenshots on failure
```

## What the E2E Tester Does

1. **Creates** Playwright test scripts
2. **Runs** browser-based tests
3. **Captures** screenshots on failure
4. **Reports** test results and issues

## Output

The E2E tester provides:
- Test execution results
- Failed test analysis
- Screenshots (if failures)
- Recommendations for fixes

## Commands

```bash
# Manual commands
uv run pytest tests/e2e/ -v
uv run pytest tests/e2e/ --headed
uv run playwright codegen http://localhost:8000
```

## Related

- `/test` - Unit and integration tests
- `/coverage` - Test coverage analysis
- `@e2e-tester` - Mention in conversation
