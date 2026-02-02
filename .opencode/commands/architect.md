---
description: Invoke the architect agent for design decisions, architecture analysis, and technical planning
agent: architect
---

# /architect

Analyze architecture and make design decisions for this codebase.

## Usage

```
/architect [topic or question]
```

## Examples

```
/architect How should we structure the new caching layer?
/architect Review the current module dependencies
/architect What pattern should we use for the plugin system?
/architect Analyze trade-offs between sync and async implementation
```

## What the Architect Does

1. **Analyzes** current architecture and patterns
2. **Evaluates** design options with trade-offs
3. **Recommends** patterns and structures
4. **Documents** decisions for future reference (using supermemory)

## Output

The architect provides:
- Current state analysis
- Identified issues and risks
- Proposed changes with rationale
- Migration paths
- Decision documentation

## Related

- `/review` - Code quality review
- `/refactor` - Refactoring suggestions
- `@architect` - Mention architect in conversation
