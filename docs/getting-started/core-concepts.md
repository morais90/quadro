# Core Concepts

You just created your first task and saw it's a markdown file. Let's understand how this works and what you can do with it.

## What a task looks like

Open `tasks/1.md` in your editor. You'll see two parts.

The top has YAML frontmatter. This is what Quadro reads to track your task:

```yaml
---
status: todo
created: 2024-10-17T10:00:00+00:00
milestone: null
completed: null
---
```

Below that is the markdown body. This part is yours to use however you want:

```markdown
# Implement authentication

Add JWT-based authentication to the API.

## Notes
Using the jsonwebtoken library. Tokens expire after 24 hours.

## Checklist
- [x] Create token generation endpoint
- [ ] Add middleware to verify tokens
- [ ] Write integration tests
```

You can add notes, checklists, code snippets, links, anything markdown supports. Quadro only cares about the frontmatter. The rest is for you.

## How tasks flow

Every task goes through three states: `TODO → PROGRESS → DONE`

New tasks start as `TODO`. When you run `quadro start 1`, the status changes to `PROGRESS`. When you run `quadro done 1`, it becomes `DONE` and Quadro adds a completion timestamp.

That's the whole workflow. Simple and clear.

## Three ways to work

You can manage tasks in three ways, and they all work together.

**From the terminal**: Run `quadro add "Fix bug"` or `quadro start 5`. Quick commands for quick updates.

**Edit files directly**: Open `tasks/3.md` in VS Code or vim. Change the title, add notes, update your checklist. Save it. Quadro sees your changes.

**Through your AI assistant**: When you're working with Claude, you can say "Create a task to add input validation" and Claude will use Quadro to add it. Later you say "Start task 7" and Claude marks it in progress. You finish it and say "Mark task 7 as done." Your tasks stay in sync with your conversation.

The important part: all three work on the same files. Use the CLI when you want speed. Edit files when you want detail. Let your AI help when you're in flow.

## Organizing with milestones

Milestones are folders inside `tasks/`. They help you group related work.

Your project might look like this:

```
your-project/
├── tasks/
│   ├── 1.md
│   ├── 2.md
│   └── MVP/
│       ├── 3.md
│       └── 4.md
├── src/
└── README.md
```

You can organize by sprint, version, or work area. Whatever makes sense for your project. Milestones are just directories. Create them when you need them.

Task IDs stay unique across everything. Task 3 is task 3, whether it's in `MVP/` or `tasks/` root.

## How AI integration works

Quadro includes a Model Context Protocol server. When you set this up, your AI assistant can read and write your tasks directly.

You're coding with Claude and discussing your project:

**You**: "We should add rate limiting. Use Quadro to create a task for this."
**Claude**: "Created task #8: Add rate limiting to API endpoints"

**You**: "Use Quadro to start task 8"
**Claude**: "Task #8 in progress. What approach do you want for rate limiting?"

You work together on the code. When you're done:

**You**: "Use Quadro to mark task 8 done"
**Claude**: "Task #8 done. Added completion timestamp"

Be direct when you want Claude to use Quadro. Say "Use Quadro to create a task" or "Use Quadro to start task 5." This tells Claude to actually use the MCP tools, not just acknowledge your request.

Your task board stays in sync while you focus on code. No manual updates. No switching tools.

## What's next

Now you understand how tasks work. Set up MCP integration to work with your AI assistant, or check out the CLI reference to learn all available commands.

[MCP Integration →](../mcp.md){ .md-button .md-button--primary }
[CLI Reference →](../cli.md){ .md-button }
