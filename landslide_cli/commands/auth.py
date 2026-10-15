import click

from ..client import LandslideClient
from ..config import get_auth_token


@click.group(name="auth")
def auth():
    """Manage authentication status and tokens."""
    pass


@auth.command(name="status")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def status(ctx, api_url):
    """Show current authentication status."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.get_auth_status()
        click.echo(f"API Status: {result.get('status', 'unknown')}")
        click.echo(f"Authenticated: {result.get('authenticated', result.get('healthy', False))}")
    except Exception:
        token = get_auth_token()
        if token:
            click.echo("Token present but API unreachable (stored credentials)")
        else:
            click.echo("Not authenticated. Run 'landslide login' first.")


@auth.command(name="token")
def show_token():
    """Display the current auth token."""
    token = get_auth_token()
    if token:
        click.echo(token)
    else:
        click.echo("No token found. Run 'landslide login' first.", err=True)
        raise click.Abort()
