import json

import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="devices", help="Manage devices.")
def devices():
    pass


@devices.command(name="list")
@click.option("--limit", "-l", type=int, default=20, help="Max results")
@click.option("--status", "-s", default=None, help="Filter by status")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_devices(ctx, limit, status, api_url):
    """List devices."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_devices(limit=limit, status=status)
        items = result if isinstance(result, list) else result.get("devices", result.get("items", []))
        if not items:
            click.echo("No devices found.")
            return
        rows = [[d.get("id", "")[:12], d.get("name", ""), d.get("type", ""), d.get("status", "")] for d in items]
        click.echo(tabulate(rows, headers=["ID", "Name", "Type", "Status"]))
    except Exception as e:
        click.echo(f"Failed to list devices: {e}", err=True)
        raise click.Abort()


@devices.command(name="create")
@click.option("--name", "-n", required=True, help="Device name")
@click.option("--type", "-t", required=True, help="Device type")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def create_device(ctx, name, type, api_url):
    """Create a new device."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {"name": name, "device_type": type}
    try:
        result = client.create_device(data)
        click.echo(f"Device created: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to create device: {e}", err=True)
        raise click.Abort()


@devices.command(name="get")
@click.argument("device-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def get_device(ctx, device_id, api_url):
    """Get device details by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        click.echo(json.dumps(client.get_device(device_id), indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get device: {e}", err=True)
        raise click.Abort()


@devices.command(name="register")
@click.option("--name", "-n", required=True, help="Device name")
@click.option("--type", "-t", required=True, help="Device type")
@click.option("--address", "-a", default="", help="Device address")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def register_device(ctx, name, type, address, api_url):
    """Register a device."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {"name": name, "device_type": type, "address": address}
    try:
        result = client.register_device(data)
        click.echo(f"Device registered: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to register device: {e}", err=True)
        raise click.Abort()


@devices.command(name="status")
@click.argument("device-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def device_status(ctx, device_id, api_url):
    """Get device status by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        click.echo(json.dumps(client.get_device_status(device_id), indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get device status: {e}", err=True)
        raise click.Abort()
