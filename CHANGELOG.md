# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).
While the project is `0.x`, minor versions may change behaviour; security-relevant changes are always listed.

## [Unreleased]

### Added
- Bundled Semgrep rules for JavaScript/TypeScript, Go and Java and more Python checks (25 rules, each with a
  positive and a negative test run by `semgrep --test`); generated reference in `docs/semgrep-rules.md`.
- Vulnerability database age: the report records Trivy's last-update time, offline scans on a database older than
  7 days warn, and `[scan] max_db_age_days` fails closed.
- `reposcan --version`; a clear error on unsupported platforms (Windows).
- `Dockerfile` and a CI-verified isolation recipe (`--network none`, read-only root, non-root).
- `scripts/verify_pins.py` (checks every pinned action against its upstream tag), `docs/repository-settings.md`.
- CI: macOS unit tests, container isolation, release rehearsal, weekly all-scanner network job with dogfooding,
  full-history secret scan.

### Changed
- **The distribution is named `reposcan-orchestrator`** (the import package and command are still `reposcan`).
  PyPI already hosts unrelated packages called `reposcan` and `repo-security-scanner`; this project is not
  published there. Install from a pinned Git commit or tag.
- Dependency floors raised to the tested versions; `hatchling` 1.32.4.
- Wheel metadata: SPDX licence expression, project URLs, `py.typed` marker.

### Security
- Closed repository-controlled suppression channels: `# nosemgrep` (`--disable-nosem`), inline `trivy:ignore` /
  `tfsec:ignore` (fail closed), `.gitleaksignore` (fail closed), `osv-scanner.toml` (empty `--config`).
- Removed documentation that told users to `pip install reposcan` (dependency-confusion hazard) and added tests
  that reject it.

## [0.1.0] - 2026-10-16

Initial version: Gitleaks, Semgrep, Trivy and OSV-Scanner adapters; unified findings; baselines and suppressions
with owner, reason and expiry; JSON, HTML, SARIF, Markdown and Code Quality reports; severity policy and exit codes;
documentation, walkthrough and CI definitions.
