# Classroom CLI Agent (cca) – Ollama-based

Default model: `devstral-small-2:24b-cloud`

Override options:
- `--model <name>`
- `OLLAMA_MODEL` environment variable

---

## Start Ollama and pull a model

```bash
ollama serve
ollama pull devstral-small-2:24b-cloud
```

---

## Install

```bash
pip install -e .
```

---

## What this tool does

This simplified CLI intentionally exposes **only two commands**:

1. **`create`**  
   Generate or update a single Python source module from a natural-language description.

2. **`commit`**  
   Stage changes and create a Git commit, with an optional push.

---

## Command overview

### `create`

Generate or update a single Python source module from a natural-language description.

- Writes code under your repo (typically `src/`)
- Overwrites the target module file
- Does not run tests
- Does not commit

```bash
cca --repo <repo> create \
  --desc "<natural language description>" \
  --module <path/to/module.py>
```

Common flags:
- `--model <name>` to override the Ollama model
- `--verbose` for more logging

---

### `commit`

Persist changes to version control.

- Runs `git add -A`
- Creates a commit with the provided message
- Optionally pushes to the configured remote

```bash
cca --repo <repo> commit \
  --message "<commit message>" \
  --push
```

---

## Example workflow

```bash
cca --repo output/demo_calculator --verbose create --desc "A calculator with add, subtract, multiply, divide functions"  --module src/calculator.py

cca --repo output/demo_calculator commit  --message "Add calculator module"  --push
```

```bash
cca --repo output/demo_streamlit_calculator --verbose create --desc "A streamlit calculator project"  --module src/calculator.py

cca --repo output/demo_streamlit_calculator commit  --message "Add calculator module"  --push
```

```bash
cca --repo output/demo_streamlit_prime_checker --verbose create --desc "A streamlit prime checker project"  --module src/prime.py

cca --repo output/demo_streamlit_prime_checker commit  --message "Add prime checker in streamlit"  --push
```
