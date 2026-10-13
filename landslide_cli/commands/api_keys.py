import click

from ..client import LandslideClient


@click.group(name="api-keys", help="Manage API keys for programmatic access.")
def api_keys():
    pass


@api_keys.command(name="list")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_keys(ctx, api_url):
    """List all API keys."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        keys = client.list_api_keys()
        if not keys:
            click.echo("No API keys found.")
            return
        for key in keys if isinstance(keys, list) else keys.get("api_keys", []):
            click.echo(f"  {key.get('id', '?'):<40} {key.get('name', '?'):<30} "
                       f"created: {key.get('created_at', '?')}")
    except Exception as e:
        click.echo(f"Failed to list API keys: {e}", err=True)
        raise click.Abort()


@api_keys.command(name="create")
@click.option("--name", "-n", required=True, help="Key name")
@click.option("--permissions", "-p", multiple=True,
              type=click.Choice(["read", "write", "admin"]),
              help="Permissions (repeatable)")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def create_key(ctx, name, permissions, api_url):
    """Create a new API key."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        perms = {p: True for p in permissions} if permissions else None
        result = client.create_api_key(name, perms)
        click.echo(f"API key created: {result.get('key', 'N/A')}")
        click.echo("Store this securely - it will not be shown again.")
    except Exception as e:
        click.echo(f"Failed to create API key: {e}", err=True)
        raise click.Abort()


@api_keys.command(name="rotate")
@click.argument("key-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def rotate_key(ctx, key_id, api_url):
    """Regenerate an API key by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.rotate_api_key(key_id)
        click.echo(f"Key rotated. New key: {result.get('key', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to rotate key: {e}", err=True)
        raise click.Abort()


@api_keys.command(name="update")
@click.argument("key-id")
@click.option("--name", "-n", help="New key name")
@click.option("--permissions", "-p", multiple=True,
              type=click.Choice(["read", "write", "admin"]),
              help="Permissions (repeatable)")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def update_key(ctx, key_id, name, permissions, api_url):
    """Update an API key's name or permissions."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {}
    if name:
        data["name"] = name
    if permissions:
        data["permissions"] = {p: True for p in permissions}
    try:
        result = client.update_api_key(key_id, data)
        click.echo(f"API key {key_id} updated.")
    except Exception as e:
        click.echo(f"Failed to update key: {e}", err=True)
        raise click.Abort()


@api_keys.command(name="revoke")
@click.argument("key-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def revoke_key(ctx, key_id, api_url):
    """Revoke (delete) an API key."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        client.revoke_api_key(key_id)
        click.echo(f"API key {key_id} revoked.")
    except Exception as e:
        click.echo(f"Failed to revoke key: {e}", err=True)
        raise click.Abort()


@api_keys.command(name="stats")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def key_stats(ctx, api_url):
    """Show API key usage statistics."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        stats = client.get_api_key_stats()
        if isinstance(stats, dict) and "error" in stats:
            click.echo(f"Stats not available: {stats['error']}")
        else:
            for k, v in (stats.items() if isinstance(stats, dict) else stats):
                click.echo(f"{k}: {v}")
    except Exception as e:
        click.echo(f"Failed to get key stats: {e}", err=True)
        raise click.Abort()
