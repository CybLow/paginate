import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Find unused imports in Python files using ruff. Returns list of files with unused imports that can be auto-fixed.",
  args: {
    path: tool.schema.string().optional().describe("File or directory to check (default: src/)"),
    fix: tool.schema.boolean().optional().describe("Auto-fix unused imports (default: false, just report)"),
  },
  async execute(args, context) {
    const targetPath = args.path || "src/"
    const fullPath = path.join(context.worktree, targetPath)
    const fix = args.fix || false
    
    try {
      let result: string
      
      if (fix) {
        result = await Bun.$`uv run ruff check ${fullPath} --select F401 --fix`.text()
        return `## Unused Imports Fixed\n\n` +
          "```\n" + (result || "All unused imports have been removed.") + "```\n\n" +
          "Run `git diff` to see the changes."
      } else {
        result = await Bun.$`uv run ruff check ${fullPath} --select F401`.text()
        
        if (!result.trim()) {
          return `No unused imports found in ${targetPath}. Code is clean!`
        }
        
        return `## Unused Imports Report for ${targetPath}\n\n` +
          "```\n" + result + "```\n\n" +
          "### To auto-fix:\n" +
          "Run this tool with `fix: true` or manually run:\n" +
          "```bash\n" +
          `uv run ruff check ${targetPath} --select F401 --fix\n` +
          "```"
      }
    } catch (error) {
      const errorStr = String(error)
      // Ruff returns non-zero when issues found
      if (errorStr.includes("F401")) {
        return `## Unused Imports Found\n\n` +
          "```\n" + errorStr + "```\n\n" +
          "Run with `fix: true` to auto-remove unused imports."
      }
      return `Error running ruff: ${error}`
    }
  },
})
