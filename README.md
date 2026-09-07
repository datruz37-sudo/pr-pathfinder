# pr-pathfinder

[![CI](https://github.com/datruz37-sudo/pr-pathfinder/actions/workflows/ci.yml/badge.svg)](https://github.com/datruz37-sudo/pr-pathfinder/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://github.com/datruz37-sudo/pr-pathfinder/actions/workflows/scorecard.yml/badge.svg)](https://github.com/datruz37-sudo/pr-pathfinder/actions/workflows/scorecard.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

`pr-pathfinder` is a local, explainable CLI that finds friction in an open-source repository's
first-contributor journey.

It does not execute project code, call an external API, upload repository content, or turn
community health into a mysterious score. Every finding names the evidence, explains why it
matters, and recommends a concrete fix.

> Project status: early alpha. It is intended to grow through reviewed community contributions.

## Why this exists

A repository can have excellent code and still be difficult to contribute to. Newcomers often
lose time looking for setup steps, guessing which checks CI expects, or discovering that security
and conduct contacts are missing. Maintainers usually notice these gaps only after a contributor
gives up.

`pr-pathfinder` makes that path testable before someone has to struggle through it.

## Quick start

Python 3.11 or newer is required.

```bash
python -m pip install pr-pathfinder
pr-pathfinder check .
```

Machine-readable and CI-friendly reports are built in:

```bash
pr-pathfinder check . --format json --fail-on error
pr-pathfinder check . --format markdown --fail-on warning
pr-pathfinder check . --format sarif --fail-on warning
pr-pathfinder rules
```

SARIF 2.1.0 output is suitable for CI and code-scanning integrations. The command only reads the
target checkout; uploading the resulting file is an explicit choice of the surrounding workflow.

## Configuration

Some rules are right in general but wrong for a specific project. Add an optional
`pr-pathfinder.toml` next to the repository root. You can scan only selected rules, ignore
specific rules, or adjust severity without changing the scanner's built-in defaults:

```toml
include = ["community/license", "agentready/instructions"]
ignore = ["community/license"]

[severity]
"automation/continuous-integration" = "error"
"agentready/instructions" = "info"
```

Run `pr-pathfinder rules` to list stable identifiers. `ignore` wins when a rule appears in
both lists. Unknown ids in `include` and `severity` are rejected with an error, as are
unknown settings and severity values; unknown ids in `ignore` only print a warning, so
renaming a rule never breaks existing configs. An empty `include` list is rejected: it
would silently disable every check. Valid severities are `info`, `warning`, and `error`.
Without the file, every rule runs at its built-in severity: the default behaviour never
changes.

Machine-readable reports carry `schema_version` (currently `1`) and `tool_version`, so
consumers can detect format changes. Finding locations are repository-relative; the
absolute checkout path is shown only in terminal output, never in JSON or SARIF.

## Baseline: adopt gradually

A large repository rarely starts clean. Record the current findings once, then get
alerted only about new ones:

```bash
pr-pathfinder check . --write-baseline baseline.json
pr-pathfinder check . --baseline baseline.json --fail-on warning
```

The baseline file stores stable finding fingerprints (rule, location, title — no machine
paths), so it works across machines and in CI. Fixed findings simply disappear from
later reports; unknown entries are ignored.

## Changed files: check pull requests incrementally

Report only findings that touch files changed in a pull request:

```bash
git diff --name-only origin/main...HEAD > changed.txt
pr-pathfinder check . --changed-files changed.txt --fail-on warning
```

Entries are repo-relative paths (directories match everything beneath them); findings
that cannot be attributed to a file are always shown. Combine with `--baseline` to
ignore both old and untouched findings.

For local development, clone the repository and install it in editable mode
(`python -m pip install -e .`) in an isolated environment.

## What the first release checks

- README, license, contributor guide, code of conduct, and security policy presence
- actionable setup, test, and pull-request guidance in `CONTRIBUTING.md`
- a private conduct-reporting route
- issue and pull-request templates
- pull-request CI that appears to run a test, check, lint, or build step
- documented npm scripts that `package.json` does not define
- documented Python dev tools that no packaging file declares
- instructions for automated readers (`AGENTS.md` or `CLAUDE.md`)
- text files too large to be read in a single pass
- documented `make` targets that have no `Makefile` behind them
- a changelog recording what changed between releases
- contributor guides showing at least one runnable command

The first release intentionally uses conservative, local checks. A missing file does not prove a
project is unhealthy, and a present file does not prove its process works. Findings are review
prompts, not moral judgments.

## Output philosophy

- **Explainable:** each rule has a stable identifier and remediation.
- **Deterministic:** the same local tree produces the same result.
- **Private:** source contents stay on the machine.
- **Safe by default:** scanning never executes the target repository.
- **Extensible:** a rule is a small Python object plus focused fixtures and tests.

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the
[first contribution guide](docs/first-contribution.md). Rule proposals should describe real
contributor friction and deterministic evidence. We will not split one change into artificial PRs
or accept low-value patches merely to inflate contributor metrics.

Good contributions include:

- a well-evidenced rule with positive and negative fixtures;
- support for a new ecosystem's conventional files;
- clearer remediation copy;
- accessibility or localization improvements;
- reporter and CI integrations that preserve offline behavior.

## Roadmap

See [ROADMAP.md](ROADMAP.md). Near-term work focuses on configuration, ecosystem-aware checks,
SARIF output, and realistic fixture repositories.

## License

MIT. See [LICENSE](LICENSE).
