import json

import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="scenes", help="Manage scenes.")
def scenes():
    pass


@scenes.command(name="list")
@click.option("--limit", "-l", type=int, default=20, help="Max results")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_scenes(ctx, limit, api_url):
    """List scenes."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_scenes(limit=limit)
        items = result if isinstance(result, list) else result.get("scenes", result.get("items", []))
        if not items:
            click.echo("No scenes found.")
            return
        rows = [[s.get("id", "")[:12], s.get("name", ""), s.get("status", "")] for s in items]
        click.echo(tabulate(rows, headers=["ID", "Name", "Status"]))
    except Exception as e:
        click.echo(f"Failed to list scenes: {e}", err=True)
        raise click.Abort()


@scenes.command(name="create")
@click.option("--name", "-n", required=True, help="Scene name")
@click.option("--description", "-d", default="", help="Description")
@click.option("--domains", required=True, help="Comma-separated domains")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def create_scene(ctx, name, description, domains, api_url):
    """Create a new scene."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {"name": name, "description": description, "domains": [d.strip() for d in domains.split(",")]}
    try:
        result = client.create_scene(data)
        click.echo(f"Scene created: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to create scene: {e}", err=True)
        raise click.Abort()


@scenes.command(name="get")
@click.argument("scene-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def get_scene(ctx, scene_id, api_url):
    """Get scene details by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        click.echo(json.dumps(client.get_scene(scene_id), indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get scene: {e}", err=True)
        raise click.Abort()
