# Quickstart

Let's create your first task and see how Quadro works.

## Create a task

```bash
quadro add "Set up development environment"
```

Done. Quadro created task #1.

## Here's the interesting part

Look at your project folder. You now have a `tasks/` directory with a file called `1.md`. Open it:

```markdown
---
status: todo
created: 2024-10-17T10:00:00+00:00
milestone: null
completed: null
---

# Set up development environment
```

That's your task. Just a markdown file. You can read it, edit it, track it in git. Nothing magic. This is why your AI assistant can work with it too.

## See your tasks

```bash
quadro list
```

Quadro shows you a nice table:

```
┌────┬──────────────────────────────────────┬──────────┬───────────┬─────────────────────┐
│ ID │ Title                                │ Status   │ Milestone │ Created             │
├────┼──────────────────────────────────────┼──────────┼───────────┼─────────────────────┤
│ 1  │ Set up development environment       │ TODO     │           │ 2024-10-17 10:00:00 │
└────┴──────────────────────────────────────┴──────────┴───────────┴─────────────────────┘
```

## Start working on it

```bash
quadro start 1
```

The task status changes to `PROGRESS`. If you look at `tasks/1.md` again, you'll see the status updated there too.

## Mark it done

```bash
quadro done 1
```

Status changes to `DONE`. Quadro adds a completion timestamp automatically.

## That's the basic flow

Add tasks. Start them. Complete them. Everything is stored in simple files you can open, edit, and track with git.

Want to understand how milestones work, or how to organize larger projects? The core concepts guide explains all of that.

[Learn core concepts →](core-concepts.md){ .md-button .md-button--primary }
