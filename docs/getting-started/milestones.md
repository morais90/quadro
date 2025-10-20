# Working with Milestones

Milestones are folders inside `tasks/` that group related work. You don't need them for small projects. But when your task list grows, they help you organize.

```
tasks/
├── 1.md
├── 2.md
├── MVP/
│   ├── 3.md
│   └── 4.md
└── Documentation/
    └── 5.md
```

Tasks at the root level don't belong to any milestone. That's fine for quick fixes and small tasks.

## How this works in practice

Say you're building a CLI tool for environment variables. You want to ship a first version, then add features later.

Create tasks for the core functionality:

```bash
quadro add "Read .env files" --milestone MVP
quadro add "Set variables in shell" --milestone MVP
quadro add "List current variables" --milestone MVP
```

These go in an MVP milestone. They're the essentials you need for launch.

As you work, you need documentation:

```bash
quadro add "Write README" --milestone Documentation
quadro add "Add usage examples" --milestone Documentation
```

You get ideas for future improvements:

```bash
quadro add "Support multiple file formats" --milestone "v2.0"
quadro add "Add encryption for secrets" --milestone "v2.0"
```

These go in v2.0 because they're not needed for launch.

Small tasks come up that don't fit anywhere:

```bash
quadro add "Fix typo in help text"
quadro add "Update dependencies"
```

These stay at root. Not everything needs a milestone.

Your structure now looks like this:

```
tasks/
├── 1.md                    # Quick fixes
├── 2.md
├── MVP/                    # Core features
│   ├── 3.md
│   ├── 4.md
│   └── 5.md
├── Documentation/          # Docs work
│   ├── 6.md
│   └── 7.md
└── v2.0/                  # Future features
    ├── 8.md
    └── 9.md
```

## Ways to organize

The example above uses versions (MVP, v2.0) and areas (Documentation). You could also organize by sprint (Sprint-1, Sprint-2), by phase (Research, Development, Testing), or by team (Backend, Frontend, Infrastructure).

Use what matches how you think about your project.

## Moving tasks between milestones

Projects change. What seemed like MVP work might move to v2.0:

```bash
quadro move 5 v2.0
```

Or something from v2.0 becomes urgent:

```bash
quadro move 8 MVP
```

The structure should serve you, not constrain you. Reorganize when it makes sense.

## A few tips

Keep milestone names short and clear. `MVP` is better than `Initial-Release-Candidate-Version-1`.

Don't create too many milestones. If you have ten active milestones, you're probably organizing too much. Three to five is usually enough.

Don't organize too early. Start with tasks at root level. Add milestones when you feel the need, not because you think you should.

When you finish all tasks in a milestone, the folder stays there as a record. You can delete it if you want, but keeping it preserves history.

## Using milestones with your AI assistant

When working with Claude, you can tell it to organize tasks:

**You**: "Use Quadro to create a task for API authentication. Put it in MVP."
**Claude**: "Created task #12 in MVP: Implement API authentication"

**You**: "Use Quadro to move task 5 to v2.0"
**Claude**: "Moved task #5 to v2.0"

This works the same way as the CLI. Your AI can create tasks in milestones and move them around.
