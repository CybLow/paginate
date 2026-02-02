import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Check for outdated or vulnerable dependencies. Returns a report of packages that need attention.",
  args: {
    check: tool.schema.enum(["all", "outdated", "security"]).optional().describe("What to check: all, outdated, or security. Default: all"),
  },
  async execute(args, context) {
    const check = args.check || "all"
    let report = "## Dependency Check Report\n\n"
    
    try {
      if (check === "all" || check === "outdated") {
        report += "### Outdated Packages\n\n"
        try {
          const outdated = await Bun.$`uv pip list --outdated`.text()
          if (outdated.trim()) {
            report += "```\n" + outdated + "```\n\n"
          } else {
            report += "All packages are up to date.\n\n"
          }
        } catch (e) {
          report += "Could not check outdated packages.\n\n"
        }
      }
      
      if (check === "all" || check === "security") {
        report += "### Security Vulnerabilities\n\n"
        try {
          const audit = await Bun.$`uv run pip-audit --progress-spinner off`.text()
          if (audit.includes("No known vulnerabilities found")) {
            report += "No known security vulnerabilities found.\n\n"
          } else {
            report += "```\n" + audit + "```\n\n"
          }
        } catch (e) {
          // pip-audit returns non-zero exit code when vulnerabilities found
          const errorOutput = String(e)
          if (errorOutput.includes("vulnerability") || errorOutput.includes("PYSEC") || errorOutput.includes("GHSA")) {
            report += "```\n" + errorOutput + "```\n\n"
          } else {
            report += "Could not run pip-audit. Install with: uv add --dev pip-audit\n\n"
          }
        }
      }
      
      report += "### Recommendations\n\n"
      report += "1. **Security issues**: Update immediately\n"
      report += "2. **Major updates**: Review changelog before updating\n"
      report += "3. **Minor/Patch updates**: Generally safe to update\n"
      
      return report
    } catch (error) {
      return `Error checking dependencies: ${error}`
    }
  },
})
