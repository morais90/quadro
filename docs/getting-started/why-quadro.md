# Why Quadro

If you work with an AI assistant to code, you probably describe what you want and your AI helps build it. The problem is those descriptions live in your head or in scattered comments. Your AI can't see them unless you paste them into the conversation every time.

Quadro stores those descriptions as markdown files. Your AI can read them through MCP. You write what needs to be built, your AI sees it and helps you implement it.

The descriptions stay in your repo. Version controlled. Always there.

## How it works

### Your AI reads your tasks

Quadro uses the [Model Context Protocol](https://modelcontextprotocol.io). AI assistants that support MCP can read your tasks.

You create a task: "Add JWT authentication to /api/login endpoint. Tokens expire after 24 hours. Use bcrypt for password hashing."

When you ask your AI to help with task #5, it can read the full description and requirements. When you finish, mark it done. The task stays in your repo as a record of what was built.

### Tasks are markdown files

Each task is a markdown file with some YAML at the top for metadata.

```markdown
---
status: progress
created: 2024-10-06T12:00:00+00:00
milestone: MVP
---

# Implement user authentication

Add JWT-based authentication to the API.

## Requirements
- POST /api/login endpoint accepts email and password
- Returns JWT token valid for 24 hours
- Use bcrypt for password hashing
- Add middleware to verify tokens on protected routes
```

You can open these files in any editor. Track them with git. Search them with grep. When a task is done, it documents what was built.

### Terminal interface

Manage tasks from the command line:

```bash
quadro add "Fix login bug"
quadro start 42
quadro done 42
```

Commands run locally. No servers, no API calls.

Use the CLI for quick updates. Let your AI read and manage tasks when you're coding together. Edit the markdown files directly when you want to add details.

Learn more about [MCP Integration](../mcp.md) or jump to [CLI commands](../cli.md).

## Why markdown files?

Why not use a database or web API?

Files are simpler. Your AI can read them. Git can track them. Any editor can open them. They work offline. You own them.

Quadro uses the simplest format that works with your existing tools.

## What about teams?

Right now, Quadro works best for solo developers or small teams that share a git repository.

We're planning to add GitHub Issues sync so you can work locally and sync with your team's issue tracker when needed. This isn't ready yet.

For now, if your team already shares code through git, you can commit your tasks and push them just like code.

## Try it

If you code with an AI assistant and want it to see your task list, Quadro might work for you.

[Get started →](installation.md){ .md-button .md-button--primary }
