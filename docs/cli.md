# CLI Reference

Need a quick command? Here's everything Quadro can do from the terminal.

## How this fits together

You have three ways to work with tasks: use these CLI commands, edit the markdown files directly, or let your AI assistant manage them through MCP. All three work with the same files in your `tasks/` directory.

This page covers the CLI commands. Use them when you want quick, direct control.

**Quick tip**: Running `quadro` without any command defaults to `quadro list`.

## Commands

::: quadro.cli.add

::: quadro.cli.list_tasks

::: quadro.cli.start

::: quadro.cli.done

::: quadro.cli.show

::: quadro.cli.milestones

::: quadro.cli.move

::: quadro.cli.edit

::: quadro.cli.delete

## Environment Variables

The `edit` command uses your `EDITOR` environment variable. Set it in your shell profile:

```bash
export EDITOR=vim
# or
export EDITOR="code --wait"
```

If you don't set `EDITOR`, Quadro will try common editors like vim, nano, or vi.

## Exit Codes

Commands return standard exit codes:

- `0` means success
- `1` means something went wrong (task not found, file error, etc.)

Useful if you're using Quadro in scripts.

## Getting Help

Every command shows help with the `--help` flag:

```bash
quadro --help
quadro add --help
quadro list --help
```
