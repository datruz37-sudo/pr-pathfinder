# Changelog

All notable changes will be documented here. The format follows Keep a Changelog, and releases aim
to follow Semantic Versioning after the public API stabilizes.

## [Unreleased]

### Added

- new rules: `ecosystem/node-scripts` and `ecosystem/python-dev-tools` (documented commands must be backed by the project files)
- machine-readable reports carry `schema_version` and `tool_version`
- unknown `ignore` rule ids print a warning instead of failing the scan
- empty `include` list rejected as a configuration error
- absolute checkout path removed from JSON output
- new rules: `community/changelog` and `community/runnable-commands`
- missing-file findings list every searched location
- `bug-report.yml` and `bug-report.md` recognized as bug templates
- optional `pr-pathfinder.toml` configuration with an `ignore` list of rule ids
- initial local scanner and explainable rule model
- community-health and pull-request automation checks
- text, JSON, and Markdown output
- contributor documentation, templates, policies, and CI
