import click

from ..client import LandslideClient
from ..config import load_config, save_config


@click.command(name="login")
@click.option("--email", "-e", prompt=True, help="Account email")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Account password")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def login(ctx, email, password, api_url):
    """Authenticate with the Landslide API and store credentials."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.login(email, password)
        config = load_config()
        if api_url:
            config["api_url"] = api_url
        if "access_token" in result:
            config["auth_token"] = result["access_token"]
        save_config(config)
        click.echo("Login successful. Credentials stored in ~/.landslide/config.yaml")
    except Exception as e:
        click.echo(f"Login failed: {e}", err=True)
        raise click.Abort()
