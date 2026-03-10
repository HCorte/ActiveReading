## Quick orientation for AI coding agents

This repo is a collection of classroom exercises (Portuguese) organized by lesson folders (`aula 1`, `aula 2`, ...). Each exercise is a small, standalone CLI Python program. Use the notes below to be immediately productive when editing or adding code.

Key facts
- Language: Python 3 (code contains .py and .pyc for CPython 3.8+ / 3.10). Assume compatibility with Python 3.8+.
- Layout: top-level folders named `aula X` contain exercise subfolders; each exercise usually has a `main.py` entrypoint and 1-3 module files (e.g. `contacto.py`, `agenda.py`, `estudante.py`).
- Execution pattern: scripts import sibling modules using plain imports like `from contacto import Contact`. That means they expect to be executed with the working directory set to the exercise folder (cd into the folder then `python3 main.py`).

Design & conventions (project-specific)
- Files and identifiers use Portuguese domain names (e.g. `Estudante`, `base_dados`, `mostrar_dados`). Keep new code consistent with these names and casing.
- Small, single-file modules are the norm. Data is stored in-memory using module-level lists (e.g. `base_dados`, `contactos`). Avoid persistent storage changes unless adding a clear new feature.
- Functions that interact with users use `input()` and print directly. When adding features or tests, prefer refactoring to inject input/output (parameters or wrappers) rather than changing global patterns.
- Methods commonly use simple getters like `get_nota()` and presentation methods like `mostrar_dados()`; follow that style when adding methods.

Running and debugging
- To run an exercise: cd into the exercise folder and run the script. Example:

  cd "aula 3"
  cd "exe 2"
  python3 main.py

- Don't run top-level scripts from the repo root; many imports rely on module-relative execution.
- Tests: there are no automated tests. If you add tests, place them in the same exercise folder and use pytest (install via `pip install pytest`) — but prefer small refactors to make functions testable first.

Patterns and pitfalls to watch for
- Input parsing often assumes valid input (e.g. `int(input(...))` or `float(input(...))`). Wrap parsing in try/except when making code robust.
- Global lists hold state for the lifetime of a program run. Avoid reusing names across modules to prevent accidental shadowing.
- Mixed-language identifiers: some modules mix English/Portuguese names. Keep naming consistent within a module.

Integration points & dependencies
- There are no external services or third-party dependencies in the existing exercises. Changes that introduce dependencies should add a `requirements.txt` or document steps in the exercise folder README.

Examples (from this repo)
- `aula 3/contacto.py` defines `class Contact` with `showData()` used by `agenda.py` which stores `contactos = []` and exposes `addContact()` / `listContactos()` CLI functions.
- `aula 4/exer 3/gestao.py` uses `base_dados = []` and `Estudante` objects; common helpers: `validar_dados()`, `listar_estudantes()` and `listar_media()`.

How to modify safely (recommended workflow for agents)
1. Read the `main.py` in the specific exercise folder to understand the entrypoint. Use the folder as the working directory.
2. Keep user-facing `input()`/`print()` behavior unchanged unless adding a new, backward-compatible flag or wrapper.
3. Prefer small refactors that accept parameters (for easier unit testing) rather than editing global state usage.
4. Run the script locally by cd-ing into the exercise folder and launching `python3 main.py` to validate behavior.

If unsure, ask for clarification: which exercise folder to modify, whether adding tests is desired, and whether persistence or external deps are allowed.

Files to review first when triaging a change
- `aula */**/main.py` — entrypoints
- `aula */**/*.py` — domain modules (e.g. `contacto.py`, `estudante.py`, `carro.py`)
- `__pycache__/` presence indicates tested Python versions; prefer cross-version compatible syntax.

End of file.
