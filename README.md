# Landslide CLI

Standalone command-line tool for interacting with the Landslide REST API.

## Installation

```bash
cd cli
pip install -e .
```

## Usage

```bash
landslide --help
landslide login
landslide auth status
landslide api-keys list
landslide simulations list
landslide projects list
landslide jobs list
landslide scenarios list
landslide programs list
landslide devices list
landslide scenes list
landslide solvers list
landslide config show
```

## Commands

- `login` - Interactive authentication
- `auth status|token` - Authentication status and token management
- `api-keys list|create|rotate|update|revoke|delete|stats` - API key management
- `simulations list|create|status|stop` - Simulation management
- `projects list|create` - Project management
- `jobs list|status` - Job/execution management
- `scenarios list|create|get|fork` - Scenario management
- `programs list|create|get|delete` - Program management
- `devices list|create|get|register|status` - Device management
- `scenes list|create|get` - Scene management
- `solvers list|get|configure|status` - Solver management
- `config show|validate` - Configuration management
