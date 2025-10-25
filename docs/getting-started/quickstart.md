# Quickstart

Let's set up Quadro with your AI assistant and create your first task.

## Setup

You need to connect Quadro to your AI assistant through MCP. Here's how for Claude Code:

```bash
claude mcp add quadro --scope user --transport stdio -- uvx --from quadro python -m quadro.mcp
```

Using a different AI assistant? See the [full MCP setup guide](../mcp.md) for Cursor, Windsurf, and Cline.

That's it. Your AI can now work with Quadro.

## Create your first task

Open your AI assistant and ask it to create a task:

```
Use Quadro to create a task: "Set up development environment"
```

Your AI creates the task. Now look at your project folder. You have a `tasks/` directory with a file called `1.md`:

```markdown
---
status: todo
created: 2024-10-17T10:00:00+00:00
milestone: null
completed: null
---

# Set up development environment
```

That's your task. A markdown file. You can edit it, track it in git, grep through it. Your AI can read it.

## Work with your AI

Ask your AI to show your tasks:

```
Show me my Quadro tasks
```

Your AI reads the tasks and shows them to you.

Start working on the task:

```
Use Quadro to start task #1
```

The status changes to `PROGRESS`. The file updates. When you're done:

```
Mark Quadro task #1 done
```

Status changes to `DONE`. Quadro adds a completion timestamp.

## Why this matters

Next session, your AI still knows what you're building. No re-explaining. Ask it to show you tasks. Ask it to help implement task #5. The context persists because tasks are files in your repo.

Want to add details to a task? Open the markdown file and write what you're planning to build. Your AI reads it and gives better suggestions.

## Next steps

- Read the [MCP guide](../mcp.md) to see all the ways you can work with tasks through your AI
- Check [core concepts](core-concepts.md) to understand milestones and task organization
- Or just start using it. Create tasks for what you're building. See if planning first works for you.
