"""Output formatting helpers for CLI commands."""

from __future__ import annotations

import json
import sys
from typing import Optional

import click


def get_format(ctx: click.Context) -> str:
    """Get the output format from the Click context."""
    return (ctx.obj or {}).get("output", "table")


def is_json(ctx: click.Context) -> bool:
    """Check if JSON output is requested."""
    return get_format(ctx) == "json"


def is_yaml(ctx: click.Context) -> bool:
    """Check if YAML output is requested."""
    return get_format(ctx) == "yaml"


def is_structured(ctx: click.Context) -> bool:
    """Check if any structured output (json or yaml) is requested."""
    return get_format(ctx) in ("json", "yaml")


def print_json(data):
    """Print data as formatted JSON."""
    click.echo(json.dumps(data, indent=2, default=str))


def print_yaml(data):
    """Print data as YAML."""
    try:
        import yaml
        click.echo(yaml.safe_dump(data, default_flow_style=False, sort_keys=False))
    except ImportError:
        # PyYAML is a declared dependency, but fall back gracefully.
        click.echo(json.dumps(data, indent=2, default=str))


def print_structured(ctx: click.Context, data):
    """Print data in the requested structured format (json or yaml)."""
    fmt = get_format(ctx)
    if fmt == "yaml":
        print_yaml(data)
    else:
        print_json(data)
