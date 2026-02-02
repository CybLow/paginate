import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Get test coverage report for a specific file or the entire project. Shows which lines are covered and which are missing.",
  args: {
    file: tool.schema.string().optional().describe("Specific file to check coverage for (e.g., src/pypaginate/paginator.py)"),
    format: tool.schema.enum(["term", "html", "json"]).optional().describe("Output format: term (terminal), html, or json. Default: term"),
  },
  async execute(args, context) {
    const format = args.format || "term"

    try {
      let command: string[]

      if (args.file) {
        // Coverage for specific file
        const modulePath = args.file.replace(/\//g, ".").replace(/\.py$/, "").replace(/^src\./, "")
        command = [
          "uv", "run", "pytest",
          `--cov=${args.file.replace(/\.py$/, "").replace(/\//g, ".")}`,
          "--cov-report=term-missing",
          "--no-header", "-q"
        ]
      } else {
        // Full project coverage
        command = [
          "uv", "run", "pytest",
          "--cov=src/pypaginate",
          `--cov-report=${format === "term" ? "term-missing" : format}`,
          "--no-header", "-q"
        ]
      }

      const result = await Bun.$`${command}`.text()

      return `## Coverage Report\n\n` +
        (args.file ? `File: ${args.file}\n\n` : "Full project coverage:\n\n") +
        "```\n" + result + "```\n\n" +
        "### Coverage Guidelines:\n" +
        "- Minimum required: 85%\n" +
        "- Target: 90%+\n" +
        "- Critical paths: 100%"
    } catch (error) {
      return `Error running coverage: ${error}`
    }
  },
})
