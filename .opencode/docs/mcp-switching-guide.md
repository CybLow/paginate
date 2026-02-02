# MCP Server Switching Guide

Guide for switching semantic search tools and MCP servers.

---

## Current Setup

**Semantic Search**: CocoIndex (local PostgreSQL + pgvector)
**Memory**: Supermemory (cloud-based)

### Table Names

CocoIndex uses flow-derived table names:

| Flow | Table |
|------|-------|
| `PypaginateCodeSearch` | `pypaginatecodesearch__code_embeddings` |
| `PypaginateDocsSearch` | `pypaginatedocssearch__docs_embeddings` |

---

## Switching Semantic Search Tools

### Option 1: Replace CocoIndex with Another Tool

1. **Disable CocoIndex** in `.opencode/opencode.json`:
   ```json
   "tools": {
     "cocoindex_*": false,  // Disable
     "new_tool_*": true     // Enable replacement
   }
   ```

2. **Update documentation** in:
   - `AGENTS.md` - MCP Servers table and usage section
   - `.opencode/prompts/build.md` - MCP table and patterns

3. **Stop PostgreSQL** (if no longer needed):
   ```bash
   docker stop opencode-postgres
   docker rm opencode-postgres
   ```

### Option 2: Use Multiple Search Tools

Keep both enabled for different purposes:

```json
"tools": {
  "cocoindex_*": true,   // Project codebase
  "other_tool_*": true   // External libraries
}
```

---

## Re-indexing CocoIndex

When code changes significantly:

```bash
cd /home/skusf/PycharmProjects/pypaginate

# Load environment
export $(grep -v '^#' .env | xargs)

# Update index (will prompt for confirmation)
echo "yes" | uv run cocoindex update .opencode/scripts/cocoindex_flow.py
```

### Verify Index

```bash
# Check table counts
docker exec opencode-postgres psql -U postgres -c \
  "SELECT 'Code', COUNT(*) FROM pypaginatecodesearch__code_embeddings 
   UNION ALL 
   SELECT 'Docs', COUNT(*) FROM pypaginatedocssearch__docs_embeddings;"
```

---

## Changing Flow Names

If you rename the CocoIndex flows:

1. **Update flow file** (`.opencode/scripts/cocoindex_flow.py`):
   ```python
   @cocoindex.flow_def(name="NewFlowName")  # Change name here
   ```

2. **Update MCP server** (`.opencode/scripts/cocoindex_mcp_server.py`):
   ```python
   CODE_TABLE = "newflowname__code_embeddings"  # lowercase + __suffix
   ```

3. **Re-index**:
   ```bash
   echo "yes" | uv run cocoindex update .opencode/scripts/cocoindex_flow.py
   ```

---

## Global vs Per-Agent Configuration

### Global (Recommended)

Tools enabled/disabled for all agents in `.opencode/opencode.json`:

```json
{
  "tools": {
    "cocoindex_*": true,
    "supermemory_*": true
  }
}
```

### Per-Agent

Override in individual agent files (`.opencode/agents/*.md`):

```markdown
tools:
  cocoindex_*: false  # Disable for this agent only
```

---

## Environment Variables

Required in `.env`:

```bash
# PostgreSQL (CocoIndex)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres

# Supermemory
SUPERMEMORY_API_KEY=your_api_key_here
```

---

## Troubleshooting

### CocoIndex returns no results

1. Check PostgreSQL is running:
   ```bash
   docker ps | grep opencode-postgres
   ```

2. Check tables exist:
   ```bash
   docker exec opencode-postgres psql -U postgres -c "\dt"
   ```

3. Re-index if tables are empty:
   ```bash
   echo "yes" | uv run cocoindex update .opencode/scripts/cocoindex_flow.py
   ```

### MCP server not starting

1. Check environment variables are loaded
2. Verify `psycopg2-binary` is installed
3. Test server directly:
   ```bash
   uv run python .opencode/scripts/cocoindex_mcp_server.py
   ```

### Supermemory not working

1. Verify API key in `.env`
2. Check network connectivity
3. Verify plugin config at `~/.config/opencode/supermemory.jsonc`
