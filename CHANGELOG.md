# Changelog

All notable changes to the Landslide CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Pre-1.0 policy:** Minor versions (0.x) may include breaking changes.

## [0.1.0] - Unreleased

### Added
- Standard infrastructure modules for parity with the reference CLI tooling:
  - `exit_codes.py` — distinct exit codes: 2 (auth), 3 (not found), 4 (validation),
    5 (network), 6 (server), 7 (duplicate), 10 (not a git repo), 130 (SIGINT), 143 (SIGTERM)
  - `log.py` — stderr logging with `--verbose/-v` (INFO) and `--debug` (DEBUG) flags
  - `output.py` — table/JSON/YAML output helpers (`--output/-o`)
  - `update_check.py` — non-blocking version update check (background thread, 24h throttle,
    disabled in CI or via `LANDSLIDE_NO_UPDATE_CHECK`)
- Top-level `--no-color`, `--ci`, `--verbose/-v`, `--debug`, and `--output/-o` flags;
  CI mode auto-detected from `CI`, `GITHUB_ACTIONS`, `GITLAB_CI`
- Config validation with typo detection (`did you mean 'api_url'?`) on startup
- SIGTERM signal handling and a top-level KeyboardInterrupt handler for clean exits
- Packaging: `Makefile`, `scripts/{build_binary,build_wheel,sega_package}.sh`, and
  `.sega/README.md` for SEGA binary publishing
- `install.sh` downloads from `https://downloads.landslide.global` with SHA256SUMS verification

### Changed
- Entry point is `landslide_cli.main:main` (wraps the Click group with signal/exception
  handling and the update check); `main` is an alias-compatible callable alongside `cli`

### Existing commands
- `login`, `auth`, `api-keys`, `simulations`, `projects`, `jobs`, `config`, `scenarios`,
  `programs`, `devices`, `scenes`, `solvers`
