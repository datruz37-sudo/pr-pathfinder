# Repository conventions

Commands below are the ones CI runs. They assume Python 3.11 or newer and a
shell in the repository root.

## Setup

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## Tests

```sh
python -m pytest
```

## Lint

```sh
ruff check .
ruff format --check .
```

## Scan a repository

```sh
pr-pathfinder check .
pr-pathfinder check . --format json --fail-on error
```

## Conventions

- New rules live in `src/pr_pathfinder/rules/` and are registered in
  `src/pr_pathfinder/rules/__init__.py`.
- A rule must be deterministic: it reads the checkout, never the network, and
  never executes code from the repository being scanned.
- Every rule needs positive and negative fixtures plus focused tests.
- Every finding must point at the file that caused it.
