import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Find dead/unreachable code in Python files using vulture. Identifies unused functions, classes, variables, and imports.",
  args: {
    path: tool.schema.string().optional().describe("File or directory to analyze (default: src/)"),
    min_confidence: tool.schema.number().optional().describe("Minimum confidence percentage (0-100). Default: 80"),
  },
  async execute(args, context) {
    const targetPath = args.path || "src/"
    const fullPath = path.join(context.worktree, targetPath)
    const minConfidence = args.min_confidence || 80

    try {
      const result = await Bun.$`uv run vulture ${fullPath} --min-confidence ${minConfidence}`.text()

      if (!result.trim()) {
        return `No dead code found in ${targetPath} (confidence >= ${minConfidence}%). Code is clean!`
      }

      // Parse and categorize the output
      const lines = result.trim().split("\n")
      const unused = {
        functions: [] as string[],
        classes: [] as string[],
        variables: [] as string[],
        imports: [] as string[],
        other: [] as string[],
      }

      for (const line of lines) {
        if (line.includes("unused function")) {
          unused.functions.push(line)
        } else if (line.includes("unused class")) {
          unused.classes.push(line)
        } else if (line.includes("unused variable")) {
          unused.variables.push(line)
        } else if (line.includes("unused import")) {
          unused.imports.push(line)
        } else {
          unused.other.push(line)
        }
      }

      let report = `## Dead Code Report for ${targetPath}\n\n`
      report += `Confidence threshold: ${minConfidence}%\n\n`

      if (unused.functions.length > 0) {
        report += `### Unused Functions (${unused.functions.length})\n\`\`\`\n${unused.functions.join("\n")}\n\`\`\`\n\n`
      }
      if (unused.classes.length > 0) {
        report += `### Unused Classes (${unused.classes.length})\n\`\`\`\n${unused.classes.join("\n")}\n\`\`\`\n\n`
      }
      if (unused.variables.length > 0) {
        report += `### Unused Variables (${unused.variables.length})\n\`\`\`\n${unused.variables.join("\n")}\n\`\`\`\n\n`
      }
      if (unused.imports.length > 0) {
        report += `### Unused Imports (${unused.imports.length})\n\`\`\`\n${unused.imports.join("\n")}\n\`\`\`\n\n`
      }
      if (unused.other.length > 0) {
        report += `### Other (${unused.other.length})\n\`\`\`\n${unused.other.join("\n")}\n\`\`\`\n\n`
      }

      report += "### Notes\n"
      report += "- Review before removing: some 'dead' code may be used via dynamic imports or reflection\n"
      report += "- Create a whitelist file for false positives\n"
      report += "- Lower confidence finds more but may include false positives\n"

      return report
    } catch (error) {
      const errorStr = String(error)
      // Vulture returns non-zero when dead code found
      if (errorStr.includes("unused")) {
        return `## Dead Code Found\n\n\`\`\`\n${errorStr}\n\`\`\`\n\nReview and remove unused code.`
      }
      return `Error running vulture: ${error}. Make sure vulture is installed: uv add --dev vulture`
    }
  },
})
