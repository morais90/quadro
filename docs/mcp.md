# MCP Integration

When you work with an AI assistant, you describe what needs to be built. The problem is your AI can't see those requirements unless you paste them every time.

Quadro solves this through the Model Context Protocol. Your AI can read your tasks and see what needs to be implemented. Write your specs as tasks. Your AI reads them and helps you build.

## What is MCP?

MCP (Model Context Protocol) is a standard that lets AI assistants access tools and data. Quadro provides an MCP server that gives your AI direct access to your tasks.

Your AI can read task descriptions, see requirements, and help you implement them. When you create or update tasks through MCP, they appear as markdown files in your `tasks/` directory.

## Setup

Choose your AI assistant and follow the setup for your tool.

### Claude Code

[Claude Code](https://claude.com/code) uses a CLI to manage MCP servers. Add Quadro using the `claude mcp add` command:

```bash
claude mcp add quadro --scope user --transport stdio -- uvx --from qdr python -m quadro.mcp
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
        "qdr",
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
        "qdr",
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
   - **Args**: `--from`, `qdr`, `python`, `-m`, `quadro.mcp`

Cline will display the Quadro tools once configured.

## How to use it

You need to explicitly ask your AI assistant to use Quadro. The AI won't automatically know you want task management unless you tell it.

### Creating tasks

When you're discussing code and want to capture a task:

```
Use Quadro to create a task: "Implement JWT token generation" with description "Add function to generate and sign JWT tokens using HS256 algorithm with 1-hour expiration"
```

The task file appears in your `tasks/` directory.

Want to add it to a milestone?

```
Add this to Quadro in the MVP milestone: "Add password reset flow" with description "Implement email-based password reset: generate token, send email, validate token, update password"
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

### Updating tasks

```
Update Quadro task #5 title to "Implement JWT with refresh tokens"

Use Quadro to update task #3 description to "Add rate limiting middleware: 100 requests per 15 minutes per IP address, use Redis for tracking"

Update task #2 with title "Fix null pointer in auth middleware" and description "Handle case where user object is null after token validation fails"
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

Break down what needs to be built:

```
I need to build user authentication. Use Quadro to create these tasks in MVP:

1. "Implement JWT token generation" - Add function to create access tokens with user claims, 1-hour expiration, and HS256 signing
2. "Build login endpoint" - Create POST /api/auth/login that validates credentials and returns JWT token
3. "Add password hashing" - Use bcrypt to hash passwords with salt rounds of 12 before storing in database
```

Your AI creates the tasks with detailed descriptions. Later when you start implementing, your AI can read those task specs to help you code.

### During implementation

Ask your AI to read a task and help you implement it:

```
Show me Quadro task #5 and help me implement it
```

Then mark progress:

```
Use Quadro to start task #5
```

### Daily standup

```
Show me Quadro tasks I completed yesterday
```

### Sprint planning

```
Use Quadro to create these in Sprint-2:

1. "Refactor API handlers" - Extract common validation logic into reusable functions, reduce code duplication across endpoints
2. "Add request logging middleware" - Log all incoming requests with timestamp, method, path, IP address, and response time
3. "Improve error handling" - Standardize error responses with consistent JSON format including error code, message, and stack trace in dev mode
```

### Context switching

```
Show Quadro tasks in documentation
Mark current task done and show next in MVP
```

### Bug tracking

Found a bug while coding:

```
Use Quadro to create a task in Bugfixes: "Fix null pointer exception in auth middleware" with description "When JWT token is expired, middleware crashes instead of returning 401. Add null check after token.verify() call"
```

## Tips

Always mention "Quadro" or "using Quadro" when you want the AI to interact with your tasks. Otherwise, it might just discuss tasks without creating them.

You can request multiple operations:

```
Use Quadro to complete task #5, start task #6, and create "Write unit tests for auth endpoints" with description "Add test coverage for login, logout, and token refresh endpoints using Jest" in MVP
```

Mix task management with code discussions:

```
I just implemented the JWT token generation with refresh tokens. Mark Quadro task #1 done and show me the next task in MVP milestone.
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

When you ask your AI to use Quadro, the AI calls the MCP server, which reads or modifies markdown files in your `tasks/` directory. Changes appear in your filesystem immediately. You see them in `git diff`.

Your AI can read tasks to see what needs to be built. It can create tasks with titles, descriptions, and milestones. It can update status (TODO → PROGRESS → DONE). It can move tasks between milestones, delete tasks, and show milestone summaries.

## Troubleshooting

**AI can't find Quadro tools**: Check the MCP configuration is correct, restart your AI assistant, verify `uvx` is in your PATH.

**Permission errors**: Make sure the `tasks/` directory has read/write permissions for the user running the MCP server.

## Next steps

Try creating a task with some requirements, then ask your AI to help you implement it. See if having specs your AI can read fits your workflow.
