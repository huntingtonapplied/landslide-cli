<div align="center">
  <img src=".readme/logo.svg" alt="Landslide CLI" width="360"><br><br>
</div>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-active-success.svg)](#)

-----------------

**Landslide CLI** is the standalone command-line client for the Landslide multi-domain stochastic simulation platform — run and manage simulations, scenarios, projects and API keys against the Landslide REST API without leaving your terminal.

It authenticates against the hosted Landslide backend (API on port `8011` locally) and exposes the platform's core resources — simulations, scenarios, programs, devices, scenes and solvers — as scriptable commands.

## Install

```bash
# Published binary (recommended)
curl -fsSL https://downloads.landslide.global/cli/install.sh | bash

# Or from a clone of this repo
pip install -e .            # installs the `landslide` entry point (package: landslide-cli, not on PyPI)
```

## Authentication

```bash
landslide login            # interactive authentication
landslide auth status      # check current auth / token
landslide api-keys create  # mint a Landslide API key for scripted/CI use
```

API keys follow the `landslide_` key convention and are managed with `landslide api-keys`.

## Commands

| Command | Description |
|---------|-------------|
| `login` | Interactive authentication |
| `auth status \| token` | Authentication status and token management |
| `api-keys list \| create \| rotate \| update \| revoke \| delete \| stats` | API key management |
| `simulations list \| create \| status \| stop` | Simulation management |
| `projects list \| create` | Project management |
| `jobs list \| status` | Job / execution management |
| `scenarios list \| create \| get \| fork` | Scenario management |
| `programs list \| create \| get \| delete` | Program management |
| `devices list \| create \| get \| register \| status` | Device management |
| `scenes list \| create \| get` | Scene management |
| `solvers list \| get \| configure \| status` | Solver management |
| `config show \| validate` | Configuration management |

## Example

```bash
landslide login
landslide api-keys list
landslide simulations create --scenario my-scenario.lde
landslide simulations list
landslide config show
```

Run `landslide --help` (or `<command> --help`) for full option details.

## Documentation & resources

- API Reference — `../docs/API_REFERENCE.md` · API / Developer Guide — `../docs/API_DEVELOPER_GUIDE.md`
- Configuration Reference — `../docs/CONFIGURATION_REFERENCE.md`
- Backend API — `../backend/README.md` · project root — `../README.md`

## License

This project is licensed under the MIT License.
