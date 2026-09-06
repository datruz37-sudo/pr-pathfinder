# Contributing to pr-pathfinder

Thank you for helping make open source easier to enter. Contributions are evaluated for their
independent value, not for the number of pull requests they create.

## Before starting

1. Search existing issues and pull requests.
2. For a new rule or behavior change, open or claim an issue first.
3. Keep one coherent problem per pull request. Do not split a single fix to inflate activity.
4. Never include repository secrets, private paths, or copied proprietary content in fixtures.

## Development setup

Python 3.11 or newer is required. The package has no runtime dependencies.

```bash
python -m venv .venv
# Windows Git Bash
. .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For development checks, install the optional tools directly into that environment:

```bash
python -m pip install pytest ruff build
```

## Run checks

```bash
python -m pytest
python -m ruff check .
python -m build
python -m pr_pathfinder check . --fail-on error
```

## Add a rule

1. Choose a stable identifier such as `community/private-contact`.
2. Implement the rule under `src/pr_pathfinder/rules/`.
3. Register it in that module's `RULES` tuple.
4. Add a minimal fixture where the finding must appear.
5. Add a healthy fixture or focused unit test where it must not appear.
6. Write a recommendation that a maintainer can act on immediately.
7. Confirm the rule reads files only and never executes target-repository code.

A useful rule detects one specific obstacle. It should avoid judging project popularity, maintainer
availability, language choice, or contributor identity.

## Pull requests

In the description, explain the contributor friction, why the evidence is reliable, possible false
positives, and the commands you ran. Small patches are welcome when they solve a complete problem.
Maintainers may ask to combine tightly related patches.

AI-assisted work is welcome when disclosed. The submitting human must understand, test, and take
responsibility for the entire change. Use the attribution section in the pull-request template.

## Review expectations

Reviews prioritize safety, deterministic behavior, understandable output, tests, and contributor
experience. Maintainers will explain requested changes and avoid unexplained closures.

## Conduct and security

Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report vulnerabilities privately as described in
[SECURITY.md](SECURITY.md).

---

Initial guide initially drafted by **the maintainer**.
