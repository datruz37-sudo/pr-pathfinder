# Roadmap

This roadmap describes product gaps, not a promise of dates or a quota of pull requests.

## 0.1 — trustworthy foundation

- deterministic local scanner
- text, JSON, and Markdown reporters
- initial community-health and automation rules
- test fixtures and CI across supported Python versions
- contribution, conduct, and security policies

## 0.2 — configurable checks

- project configuration with documented precedence
- rule include/exclude support
- per-rule severity overrides
- configuration validation and migration tests

## 0.3 — ecosystem awareness

- Python command consistency checks
- Node.js command consistency checks
- Rust and Go setup conventions
- monorepo discovery with explicit boundaries

## 0.4 — CI interoperability

- SARIF reporter
- stable JSON schema
- baseline files for gradual adoption
- changed-files mode without network access

## Later exploration

- localization infrastructure
- documentation link validation with an opt-in network mode
- plugin API after the built-in rule contract is stable
- anonymized, explicitly opt-in usability research

Every item should be implemented because users need it. No roadmap item should be fragmented into
low-value changes for the purpose of manufacturing contribution metrics.

---

Initial roadmap initially drafted by **the maintainer**.
