# Code Generation CLI Agent (CCA)

CCA is a command line agent that generates Python projects from natural language descriptions.  
It supports structured planning, configurable prompt strategies, automated code generation, and Git integration.

---

## Overview

CCA enables you to:

- Generate Python applications from natural language prompts
- Choose structured planning strategies before code generation
- Select different code generation styles
- Automatically initialize and commit to Git repositories
- Operate in both command mode and interactive mode

The system is modular and prompt driven, allowing extension through YAML based prompt definitions.

---

## Requirements

- Python 3.10 or higher
- Ollama running locally
- PyYAML 6.0 or higher

---

## Installation

Install in editable mode:

```bash
pip install -e .
````

**_Reinstall after any local code modification._**


---

## Environment Configuration

Set the following environment variables:

```bash
export OLLAMA_MODEL="devstral-small-2:24b-cloud"
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_TEMPERATURE="0.0"
```

| Variable           | Description               |
| ------------------ | ------------------------- |
| OLLAMA_MODEL       | Model used for generation |
| OLLAMA_HOST        | Ollama server endpoint    |
| OLLAMA_TEMPERATURE | Sampling temperature      |

---

## Quick Start

### Interactive Mode

```bash
cca
```

You can then run commands without the `cca` prefix:

```bash
cca> create "calculator app"
cca> commit "initial commit" --repo output/project_name
cca> list-prompts
cca> exit
```

Built in interactive commands:

* help
* clear
* exit or quit

---

### Command Mode

Create a new project:

```bash
cca create "calculator with basic operations"
```

```bash
cca create "Weather App in Streamlit"
```


Use detailed planning and documented code:

```bash
cca create "web scraper" --planning detailed --codegen documented
```

Commit generated project:

```bash
cca commit "initial commit" --repo output/my_project
```

List available prompt variants:

```bash
cca list-prompts
```

Check version:

```bash
cca --version
```

---

## Commands

### create

```bash
cca create "description" [--module PATH] [--planning VARIANT] [--codegen VARIANT]
```

Options:

| Option     | Description                       |
| ---------- | --------------------------------- |
| --module   | Target module path inside project |
| --planning | Planning strategy variant         |
| --codegen  | Code generation style variant     |

If `--repo` is omitted, a timestamped directory is created under `output/`.

If `--module` is omitted, defaults to `src/main.py`.

---

### commit

```bash
cca commit [MESSAGE] --repo REPO_PATH [--push]
```

Options:

| Option  | Description                 |
| ------- | --------------------------- |
| MESSAGE | Commit message              |
| --repo  | Target repository path      |
| --push  | Push to remote after commit |

---

### list-prompts

```bash
cca list-prompts
```

Displays available planning and code generation variants.

---

## Prompt Variants

### Planning

* default
* detailed
* minimal

### Code Generation

* default
* documented
* minimal

Prompt definitions are stored in:

```
src/code_generation_cli_agent/prompts/
```

---

## Project Structure

```
code_generation_agent/
├── pyproject.toml
├── README.md
└── src/code_generation_cli_agent/
    ├── agent.py            # Core orchestration
    ├── cli.py              # Command parsing and dispatch
    ├── interactive.py      # Interactive shell loop
    ├── llm.py              # Ollama integration
    ├── prompt_manager.py   # YAML prompt loading
    ├── tools.py            # Filesystem and Git operations
    ├── types.py            # Shared type definitions
    ├── utils.py            # Common helpers
    └── prompts/
        ├── planning.yaml
        └── code_generation.yaml
```

---

## Architecture Summary

See the full documentation page for architecture details.
