# MCP Integration

You're working with Claude, deep in code. Ideas come up: refactor this module, add tests for that function, fix the edge case. Good ideas. But if you stop to create tickets, you lose flow.

That's why Quadro works with the Model Context Protocol. Your AI assistant can manage your tasks while you talk about code. No context switching. No breaking flow.

## What is MCP?

MCP (Model Context Protocol) is a standard that lets AI assistants use tools. Quadro provides an MCP server that exposes your task board to your AI.

When you tell Claude "Use Quadro to create a task," Claude actually creates it. The task appears in your `tasks/` directory as a markdown file. Your board stays in sync with your conversation.

## Setup

Choose your AI assistant and follow the setup for your tool.

### Claude Code

[Claude Code](https://claude.com/code) uses a CLI to manage MCP servers. Add Quadro using the `claude mcp add` command:

```bash
claude mcp add quadro --scope user --transport stdio -- uvx --from quadro python -m quadro.mcp
```

The `--scope user` makes Quadro available across all your projects. Use `--scope project` to add it only to the current project.

Verify the setup:

```bash
claude mcp list
```

You should see `quadro` in the list. The tools are now available in Claude Code.

### Cursor

[Cursor](https://cursor.com) supports MCP through configuration files. You can use project-specific or global configuration:

- **Project**: Create `.cursor/mcp.json` in your project directory
- **Global**: Create `~/.cursor/mcp.json` for all projects

Add this configuration:

```json
{
  "mcpServers": {
    "quadro": {
      "command": "uvx",
      "args": [
        "--from",
        "quadro",
        "python",
        "-m",
        "quadro.mcp"
      ],
      "env": {}
    }
  }
}
```

Restart Cursor. The Quadro tools will be available in your AI agent.

### Windsurf

[Windsurf](https://windsurf.com) by Codeium supports MCP through a configuration file:

- **Config file**: `~/.codeium/windsurf/mcp_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "quadro": {
      "command": "uvx",
      "args": [
        "--from",
        "quadro",
        "python",
        "-m",
        "quadro.mcp"
      ],
      "env": {}
    }
  }
}
```

Click the refresh button in Windsurf to apply the changes.

### Cline

[Cline](https://cline.bot) is a VS Code extension that supports MCP. Install the extension first, then add Quadro through Cline's configuration interface:

1. Open Cline settings in VS Code
2. Navigate to MCP servers section
3. Add a new server with these settings:
   - **Command**: `uvx`
   - **Args**: `--from`, `quadro`, `python`, `-m`, `quadro.mcp`

Cline will display the Quadro tools once configured.

## How to use it

You need to explicitly ask your AI assistant to use Quadro. The AI won't automatically know you want task management unless you tell it.

### Creating tasks

When you're discussing code and want to capture a task:

```
Use Quadro to create a task: "Implement JWT token generation"
```

The task file appears in your `tasks/` directory.

Want to add it to a milestone?

```
Add this to Quadro in the MVP milestone: "Add password reset flow"
```

### Checking your board

```
Show me my Quadro tasks
List Quadro tasks in the MVP milestone
What tasks do I have in progress using Quadro?
```

### Updating status

```
Mark Quadro task #1 as in progress
Complete Quadro task #5
Start task #3 in Quadro
```

### Moving tasks

```
Move Quadro task #8 to the v2.0 milestone
Use Quadro to move task #3 to root
```

### Deleting tasks

```
Delete Quadro task #12
Remove task #5 using Quadro
```

## Workflow examples

### Planning a feature

You're breaking down work with Claude:

```
I need to build user authentication. Use Quadro to create these tasks in MVP: JWT token generation, login endpoint, password hashing.
```

Claude creates each task. You keep planning.

### During implementation

You're coding and want to track progress:

```
Use Quadro to start task #5
```

### Daily standup

```
Show me Quadro tasks I completed yesterday
```

### Sprint planning

```
Use Quadro to create these in Sprint-2: refactor API handlers, add request middleware, improve error handling
```

### Context switching

```
Show Quadro tasks in documentation
Mark current task done and show next in MVP
```

### Bug tracking

Found a bug while coding:

```
Use Quadro to create a task in MVP: fix null pointer in auth middleware
```

## Tips

Always mention "Quadro" or "using Quadro" when you want the AI to interact with your tasks. Otherwise, it might just discuss tasks without creating them.

You can request multiple operations:

```
Use Quadro to complete task #5, start task #6, and create "Write tests" in MVP
```

Mix task management with code discussions:

```
I just implemented the JWT logic. Mark Quadro task #1 done and show me the next task in MVP.
```

Check your board periodically:

```
Show Quadro tasks grouped by milestone
List in-progress Quadro tasks
```

Keep things organized:

```
Move completed Quadro tasks from MVP to Archive
Defer Quadro tasks #8, #9, and #10 to v2.0
```

## How it works

When you ask the AI to use Quadro, the AI calls the MCP tool, which modifies markdown files in your `tasks/` directory. Changes appear in your filesystem immediately. You see them in `git diff`.

The AI can create tasks with titles, descriptions, and milestones. It can read your board with filters. It can update status (TODO → PROGRESS → DONE). It can move tasks between milestones, delete tasks, and show milestone summaries.

## Troubleshooting

**AI can't find Quadro tools**: Check the MCP configuration is correct, restart your AI assistant, verify `uvx` is in your PATH.

**Permission errors**: Make sure the `tasks/` directory has read/write permissions for the user running the MCP server.

## Next steps

Try creating a task through your AI assistant. See if it fits your workflow. Adjust your phrasing to find what feels natural.
