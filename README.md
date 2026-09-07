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
python -m pip install -e .
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
both lists. Unknown ids are rejected with an error, as are unknown settings and severity
values. Valid severities are `info`, `warning`, and `error`. Without the file, every rule
runs at its built-in severity: the default behaviour never changes.

Until the first package release, clone the repository and install it in an isolated environment.

## What the first release checks

- README, license, contributor guide, code of conduct, and security policy presence
- actionable setup, test, and pull-request guidance in `CONTRIBUTING.md`
- a private conduct-reporting route
- issue and pull-request templates
- pull-request CI that appears to run a test, check, lint, or build step
- instructions for automated readers (`AGENTS.md` or `CLAUDE.md`)
- text files too large to be read in a single pass
- documented `make` targets that have no `Makefile` behind them

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
