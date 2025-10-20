# Installation

Let's get Quadro running on your machine.

## What you need

- Python 3.12 or higher
- A terminal that supports UTF-8 (most modern terminals do)

That's it. Quadro works on macOS, Linux, and Windows.

## Choose your installation method

### Quick install with pip

If you already have Python installed, this is the fastest way:

```bash
pip install quadro
```

### Using uv (recommended for Python developers)

If you use [uv](https://github.com/astral-sh/uv) for Python package management:

```bash
uv pip install quadro
```

uv is faster than pip and handles dependencies well. If you don't have it yet, the pip method works fine.

### Install from source

Want to run the latest development version or contribute to Quadro?

```bash
git clone https://github.com/morais90/quadro.git
cd quadro
uv sync
uv run quadro
```

This clones the repository and sets up a development environment. Good for trying unreleased features or working on Quadro itself.

## Verify it works

Check that Quadro installed correctly:

```bash
quadro --version
```

You should see the version number. If you get an error, make sure Python 3.12+ is in your PATH.

## What's next

Now that Quadro is installed, let's create your first task and see how it all works.

[Quickstart guide →](quickstart.md){ .md-button .md-button--primary }
