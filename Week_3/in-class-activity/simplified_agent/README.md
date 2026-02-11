# Classroom CLI Agent

A CLI agent that generates Python code from natural language descriptions with dynamic prompts.

## Features

- Code generation from natural language
- Test generation (unittest, pytest)
- Dynamic prompt variants
- Git integration

## Requirements

- Python 3.10+
- Ollama running locally
- PyYAML 6.0+

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Interactive mode (no arguments)
cca

# Create a program
cca create "calculator with basic operations"

# With detailed planning
cca create "web scraper" --planning detailed --codegen documented

# Commit changes
cca commit --repo output/my_project

# List available prompts
cca list-prompts
```

## Interactive Mode

Run `cca` with **no arguments** to open an interactive session:

```bash
cca
```

In the interactive session, type the normal command **without** the leading `cca`.

Examples:

```bash
cca> create "calculator app"
cca> create "web scraper" --planning detailed --codegen documented
cca> commit "initial commit" --repo output/my_project
cca> list-prompts
cca> exit
```

Built-in interactive commands:
- `help`: show help
- `clear`: clear the screen
- `exit` or `quit`: exit

## Available Prompt Variants

### Planning
- `default`: Standard planning
- `detailed`: Comprehensive with architecture
- `minimal`: Quick planning

### Code Generation
- `default`: Standard code generation
- `documented`: Well-documented with type hints
- `minimal`: Concise code

## Project Structure

```
.
├── src/classroom_cli_agent/
│   ├── agent.py              # Agent logic
│   ├── cli.py                # CLI interface
│   ├── prompt_manager.py     # Prompt loading
│   └── prompts/              # YAML prompts
│       ├── planning.yaml
│       └── code_generation.yaml
└── README.md
```

## Commands

### Create
```bash
cca create "description" [--module PATH] [--planning VARIANT] [--codegen VARIANT]
```
Notes:
- If you omit `--repo`, `cca` creates a new folder under `output/` with a timestamp.
- If you omit `--module`, it defaults to `src/main.py`.

### Commit
```bash
cca commit [MESSAGE] --repo REPO_PATH [--push]
```

Notes:
- `--repo` is required for `commit`.

### List Prompts
```bash
cca list-prompts
```

### Version
```bash
cca --version
```

## Configuration

Environment variables:
```bash
export OLLAMA_MODEL="devstral-small-2:24b-cloud"
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_TEMPERATURE="0.0"
```
