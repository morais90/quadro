# Why Quadro

You're coding with your AI assistant. You're in flow. Ideas are flowing. Your AI suggests refactoring this module, adding tests for that function, updating the docs. Good ideas. You'll get to them.

But how do you track them? Open a browser, create tickets, break your flow?

That's the problem Quadro solves.

Quadro is a task manager built for how you actually work with AI. It lives in your terminal, stores tasks as markdown files, and your AI assistant can manage your tasks directly while you code. No context switching. No breaking flow.

## Three things working together

Quadro combines three simple ideas:

### Your AI assistant manages tasks

Quadro uses the [Model Context Protocol](https://modelcontextprotocol.io). AI assistants like Claude can read your tasks, create new ones, and update them while you're discussing code.

You're talking with Claude about your project. Claude suggests "We should add input validation here." Claude creates the task. You say "Let's work on task 5 now." Claude marks it as in progress. You finish it. Claude marks it done.

Your tasks stay in sync with your conversation. No manual updates. No switching tools.

### Tasks are markdown files

Each task is a markdown file. Simple text with a bit of YAML at the top.

```markdown
---
status: progress
created: 2024-10-06T12:00:00+00:00
milestone: MVP
---

# Implement user authentication

Add JWT-based authentication to the API.

## Notes
Using the jsonwebtoken library. Tokens expire after 24 hours.
```

You can read these files without Quadro. Edit them in any editor. Track them with git. Search them with grep. They're yours.

### Fast terminal interface

When you want direct control, use the CLI:

```bash
quadro add "Fix login bug"
quadro start 42
quadro done 42
```

Fast commands. Instant results. Everything runs locally.

All three work together. Use the CLI when you want quick control. Let your AI manage tasks when you're in conversation. Read and edit the files directly when you need to.

Learn more about [MCP Integration](../mcp.md) or jump to [CLI commands](../cli.md).

## Why markdown files?

You might wonder: why not a database? Why not a web API?

Simple: because AI assistants can read files. You can read files. Git can track files. Any text editor can open files. Files are portable. Files are yours.

We're not reinventing task management. We're using the simplest possible format that works with the tools you already have, including your AI assistant.

## What about team work?

Quadro is built for your local workflow first. But we know solo coding is just part of the picture.

That's why we're building sync with GitHub Issues. When you need to share tasks with your team, Quadro will bridge your local markdown files with your team's issue tracker. Work locally with your AI, sync when you're ready to collaborate.

This is coming soon. For now, Quadro works best for personal task management and small teams who share a git repository.

## Give it a try

If you code with AI assistants and want your tasks in the same flow, Quadro might fit your workflow.

[Get started →](installation.md){ .md-button .md-button--primary }
