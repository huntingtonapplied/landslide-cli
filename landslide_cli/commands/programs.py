import json

import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="programs", help="Manage programs.")
def programs():
    pass


@programs.command(name="list")
@click.option("--limit", "-l", type=int, default=20, help="Max results")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_programs(ctx, limit, api_url):
    """List programs."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_programs(limit=limit)
        items = result if isinstance(result, list) else result.get("programs", result.get("items", []))
        if not items:
            click.echo("No programs found.")
            return
        rows = [[p.get("id", "")[:12], p.get("name", ""), p.get("status", "")] for p in items]
        click.echo(tabulate(rows, headers=["ID", "Name", "Status"]))
    except Exception as e:
        click.echo(f"Failed to list programs: {e}", err=True)
        raise click.Abort()


@programs.command(name="create")
@click.option("--name", "-n", required=True, help="Program name")
@click.option("--description", "-d", default="", help="Description")
@click.option("--domains", required=True, help="Comma-separated domains")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def create_program(ctx, name, description, domains, api_url):
    """Create a new program."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {"name": name, "description": description, "domains": [d.strip() for d in domains.split(",")]}
    try:
        result = client.create_program(data)
        click.echo(f"Program created: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to create program: {e}", err=True)
        raise click.Abort()


@programs.command(name="get")
@click.argument("program-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def get_program(ctx, program_id, api_url):
    """Get program details by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        click.echo(json.dumps(client.get_program(program_id), indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get program: {e}", err=True)
        raise click.Abort()


@programs.command(name="delete")
@click.argument("program-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def delete_program(ctx, program_id, api_url):
    """Delete a program."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        client.delete_program(program_id)
        click.echo(f"Program {program_id} deleted.")
    except Exception as e:
        click.echo(f"Failed to delete program: {e}", err=True)
        raise click.Abort()
