import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Calculate cyclomatic complexity for Python files using radon. Returns complexity metrics to identify overly complex code that needs refactoring.",
  args: {
    path: tool.schema.string().describe("File or directory path to analyze (relative to project root)"),
    min_rank: tool.schema.string().optional().describe("Minimum complexity rank to show: A (simple) to F (very complex). Default: B"),
  },
  async execute(args, context) {
    const targetPath = args.path || "src/"
    const minRank = args.min_rank || "B"
    const fullPath = path.join(context.worktree, targetPath)

    try {
      const result = await Bun.$`uv run radon cc ${fullPath} -a -s --min ${minRank}`.text()

      if (!result.trim()) {
        return `No functions with complexity >= ${minRank} found in ${targetPath}. Code is well-structured!`
      }

      return `## Cyclomatic Complexity Report for ${targetPath}\n\n` +
        `Showing functions with complexity rank >= ${minRank}\n\n` +
        "```\n" + result + "```\n\n" +
        "### Complexity Ranks:\n" +
        "- A (1-5): Simple, low risk\n" +
        "- B (6-10): Moderate, acceptable\n" +
        "- C (11-20): Complex, consider refactoring\n" +
        "- D (21-30): Very complex, refactor recommended\n" +
        "- E (31-40): Extremely complex, refactor required\n" +
        "- F (41+): Untestable, must refactor"
    } catch (error) {
      return `Error running radon: ${error}. Make sure radon is installed: uv add --dev radon`
    }
  },
})
