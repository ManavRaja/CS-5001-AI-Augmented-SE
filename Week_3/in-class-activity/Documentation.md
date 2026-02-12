# Full Project Documentation

# 1. System Overview

The Code Generation CLI Agent is a modular AI driven system designed to convert natural language project descriptions into structured Python codebases.

The system operates in two primary phases:

1. Planning phase
2. Code generation phase

Both phases are controlled by configurable prompt variants.

---

# 2. Core Architecture

## 2.1 High Level Flow

User Input  
→ CLI Interface  
→ Agent Orchestrator  
→ Planning Prompt  
→ Code Generation Prompt  
→ File Writer  
→ Optional Git Commit  

---

## 2.2 Component Breakdown

### 2.2.1 cli.py

Responsibilities:
- Argument parsing
- Command dispatching
- Command mode execution

Primary commands:
- create
- commit
- list-prompts
- version

---

### 2.2.2 interactive.py

Provides:
- Persistent CLI session
- Command loop
- Built in shell commands

---

### 2.2.3 agent.py

Central orchestrator.

Responsibilities:
- Managing planning workflow
- Executing code generation workflow
- Coordinating prompt loading
- Calling LLM interface
- Writing generated output to disk

---

### 2.2.4 llm.py

Abstracts communication with Ollama.

Responsibilities:
- Reading environment configuration
- Sending prompts
- Handling temperature and model parameters
- Returning generated responses

---

### 2.2.5 prompt_manager.py

Loads YAML based prompts.

Responsibilities:
- Parsing planning.yaml
- Parsing code_generation.yaml
- Selecting variants
- Rendering prompt templates

Prompt system is fully extensible.

---

### 2.2.6 tools.py

Provides:
- Filesystem operations
- Project directory creation
- Git initialization
- Commit handling
- Optional push

---

### 2.2.7 types.py

Contains shared data models and internal type definitions.

---

### 2.2.8 utils.py

Contains shared utility functions used across modules.

---

# 3. Prompt System Design

Prompts are defined in YAML files.

Example structure:

```yaml
variants:
  default:
    system: ...
    user: ...
  detailed:
    system: ...
    user: ...
````

This allows:

* Rapid experimentation
* Controlled behavior shifts
* Extensible planning strategies
* Different code generation styles

---

# 4. Planning Strategy

Planning produces:

* Architecture overview
* File structure definition
* Functional breakdown

Variants:

| Variant  | Purpose                     |
| -------- | --------------------------- |
| default  | Balanced planning           |
| detailed | Architecture heavy planning |
| minimal  | Lightweight planning        |

---

# 5. Code Generation Strategy

Generates:

* Python modules
* Structured directories
* Optional documentation
* Type hints depending on variant

Variants:

| Variant    | Purpose                          |
| ---------- | -------------------------------- |
| default    | Clean implementation             |
| documented | Fully documented with type hints |
| minimal    | Concise code                     |

---

# 6. Git Integration Workflow

When commit is invoked:

1. Validate repository path
2. Initialize Git if not already present
3. Stage all files
4. Create commit
5. Optionally push

---

# 7. Extension Guide

## 7.1 Adding a New Prompt Variant

1. Edit planning.yaml or code_generation.yaml
2. Add new variant section
3. Restart CLI
4. Use:

```bash
cca create "description" --planning new_variant
```

---

## 7.2 Adding New Commands

1. Update cli.py
2. Add handler logic
3. Integrate into agent if necessary

---

## 7.3 Supporting Another LLM

Modify llm.py to:

* Replace Ollama client logic
* Maintain same interface signature

---

# 8. Development Workflow

1. Modify source code
2. Reinstall editable package

```bash
pip install -e .
```

3. Test in interactive mode