import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Run performance benchmarks using pytest-benchmark. Returns timing statistics for functions to compare performance before/after changes.",
  args: {
    path: tool.schema.string().optional().describe("Test file or directory to run benchmarks from (relative to project root). Default: tests/"),
    filter: tool.schema.string().optional().describe("Filter benchmarks by name pattern (e.g., 'test_paginate')"),
    compare: tool.schema.boolean().optional().describe("Compare against saved baseline. Default: false"),
    save: tool.schema.string().optional().describe("Save results with this name for future comparison"),
  },
  async execute(args, context) {
    const targetPath = args.path || "tests/"
    const fullPath = path.join(context.worktree, targetPath)
    
    let command = `uv run pytest ${fullPath} --benchmark-only -v`
    
    if (args.filter) {
      command += ` -k "${args.filter}"`
    }
    
    if (args.compare) {
      command += " --benchmark-compare"
    }
    
    if (args.save) {
      command += ` --benchmark-save="${args.save}"`
    }
    
    try {
      const result = await Bun.$`bash -c ${command}`.text()
      
      if (!result.trim()) {
        return `No benchmarks found in ${targetPath}. Add @pytest.mark.benchmark tests or use the benchmark fixture.`
      }
      
      return `## Benchmark Results for ${targetPath}\n\n` +
        "```\n" + result + "```\n\n" +
        "### Tips:\n" +
        "- Use `save` parameter to save baseline: `benchmark(path, save='baseline')`\n" +
        "- Use `compare` to compare: `benchmark(path, compare=true)`\n" +
        "- Lower min/mean times = better performance"
    } catch (error) {
      const errorStr = String(error)
      if (errorStr.includes("no benchmarks")) {
        return `No benchmark tests found in ${targetPath}.\n\n` +
          "### How to add benchmarks:\n" +
          "```python\n" +
          "def test_my_function_performance(benchmark):\n" +
          "    result = benchmark(my_function, arg1, arg2)\n" +
          "    assert result is not None\n" +
          "```"
      }
      return `Error running benchmarks: ${error}\n\nMake sure pytest-benchmark is installed: uv add --dev pytest-benchmark`
    }
  },
})
