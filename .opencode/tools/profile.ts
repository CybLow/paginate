import { tool } from "@opencode-ai/plugin"
import path from "path"

export const cpu = tool({
  description: "Profile CPU usage of Python code using py-spy. Generates flame graphs to identify hot paths and slow functions.",
  args: {
    script: tool.schema.string().describe("Python script to profile (relative to project root)"),
    duration: tool.schema.number().optional().describe("Duration in seconds to profile. Default: 10"),
    output: tool.schema.string().optional().describe("Output file name for flame graph SVG. Default: profile.svg"),
  },
  async execute(args, context) {
    const scriptPath = path.join(context.worktree, args.script)
    const duration = args.duration || 10
    const output = args.output || "profile.svg"
    const outputPath = path.join(context.worktree, output)
    
    try {
      // Check if py-spy is available
      await Bun.$`which py-spy`.text()
    } catch {
      return `py-spy is not installed. Install it with:\n\n` +
        "```bash\n" +
        "pip install py-spy\n" +
        "# or\n" +
        "brew install py-spy  # macOS\n" +
        "```\n\n" +
        "Note: py-spy may require sudo on some systems."
    }
    
    try {
      const result = await Bun.$`py-spy record -o ${outputPath} --duration ${duration} -- python ${scriptPath}`.text()
      
      return `## CPU Profile Complete\n\n` +
        `**Script**: ${args.script}\n` +
        `**Duration**: ${duration}s\n` +
        `**Output**: ${output}\n\n` +
        "### Results\n" +
        "```\n" + result + "```\n\n" +
        `Open \`${output}\` in a browser to view the flame graph.\n\n` +
        "### Reading Flame Graphs:\n" +
        "- Width = time spent in function\n" +
        "- Height = call stack depth\n" +
        "- Look for wide bars = bottlenecks"
    } catch (error) {
      return `Error profiling: ${error}`
    }
  },
})

export const memory = tool({
  description: "Profile memory usage of Python code using memray. Identifies memory leaks and high-allocation code paths.",
  args: {
    script: tool.schema.string().describe("Python script to profile (relative to project root)"),
    output: tool.schema.string().optional().describe("Output file prefix. Default: memray-profile"),
  },
  async execute(args, context) {
    const scriptPath = path.join(context.worktree, args.script)
    const output = args.output || "memray-profile"
    const binPath = path.join(context.worktree, `${output}.bin`)
    const htmlPath = path.join(context.worktree, `${output}.html`)
    
    try {
      // Run memray
      await Bun.$`uv run memray run -o ${binPath} ${scriptPath}`.text()
      
      // Generate flamegraph
      await Bun.$`uv run memray flamegraph -o ${htmlPath} ${binPath}`.text()
      
      // Get summary
      const summary = await Bun.$`uv run memray summary ${binPath}`.text()
      
      return `## Memory Profile Complete\n\n` +
        `**Script**: ${args.script}\n` +
        `**Binary**: ${output}.bin\n` +
        `**Flamegraph**: ${output}.html\n\n` +
        "### Summary\n" +
        "```\n" + summary + "```\n\n" +
        `Open \`${output}.html\` in a browser for the interactive flamegraph.\n\n` +
        "### What to Look For:\n" +
        "- High allocation counts = potential optimization targets\n" +
        "- Leaked memory = missing cleanup\n" +
        "- Large objects = memory pressure"
    } catch (error) {
      const errorStr = String(error)
      if (errorStr.includes("memray")) {
        return `memray is not installed. Install it with:\n\nuv add --dev memray`
      }
      return `Error profiling memory: ${error}`
    }
  },
})

export const scalene = tool({
  description: "Profile CPU, memory, and GPU usage with Scalene. Provides line-by-line analysis with AI-powered optimization suggestions.",
  args: {
    script: tool.schema.string().describe("Python script to profile (relative to project root)"),
    output: tool.schema.string().optional().describe("Output HTML file. Default: scalene-profile.html"),
  },
  async execute(args, context) {
    const scriptPath = path.join(context.worktree, args.script)
    const output = args.output || "scalene-profile.html"
    const outputPath = path.join(context.worktree, output)
    
    try {
      const result = await Bun.$`uv run scalene --html --outfile ${outputPath} ${scriptPath}`.text()
      
      return `## Scalene Profile Complete\n\n` +
        `**Script**: ${args.script}\n` +
        `**Output**: ${output}\n\n` +
        "### Console Output\n" +
        "```\n" + result + "```\n\n" +
        `Open \`${output}\` in a browser for detailed analysis.\n\n` +
        "### Scalene Features:\n" +
        "- Line-by-line CPU time\n" +
        "- Memory allocation tracking\n" +
        "- GPU usage (if applicable)\n" +
        "- AI-powered optimization suggestions"
    } catch (error) {
      const errorStr = String(error)
      if (errorStr.includes("scalene")) {
        return `Scalene is not installed. Install it with:\n\nuv add --dev scalene`
      }
      return `Error running Scalene: ${error}`
    }
  },
})
