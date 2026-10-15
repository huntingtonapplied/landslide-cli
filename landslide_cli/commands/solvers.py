import json

import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="solvers", help="Manage solvers.")
def solvers():
    pass


@solvers.command(name="list")
@click.option("--limit", "-l", type=int, default=20, help="Max results")
@click.option("--domain", "-d", default=None, help="Filter by domain")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_solvers(ctx, limit, domain, api_url):
    """List solvers."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_solvers(limit=limit, domain=domain)
        items = result if isinstance(result, list) else result.get("solvers", result.get("items", []))
        if not items:
            click.echo("No solvers found.")
            return
        rows = [[s.get("id", "")[:12], s.get("name", ""), s.get("domain", ""), s.get("status", "")] for s in items]
        click.echo(tabulate(rows, headers=["ID", "Name", "Domain", "Status"]))
    except Exception as e:
        click.echo(f"Failed to list solvers: {e}", err=True)
        raise click.Abort()


@solvers.command(name="get")
@click.argument("solver-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def get_solver(ctx, solver_id, api_url):
    """Get solver details by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        click.echo(json.dumps(client.get_solver(solver_id), indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get solver: {e}", err=True)
        raise click.Abort()


@solvers.command(name="configure")
@click.argument("solver-id")
@click.option("--config", "-c", required=True, help="Configuration JSON")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def configure_solver(ctx, solver_id, config, api_url):
    """Configure a solver."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        config_dict = json.loads(config)
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON config: {e}", err=True)
        raise click.Abort()
    try:
        result = client.configure_solver(solver_id, config_dict)
        click.echo(f"Solver {solver_id} configured.")
        click.echo(json.dumps(result, indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to configure solver: {e}", err=True)
        raise click.Abort()


@solvers.command(name="status")
@click.argument("solver-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def solver_status(ctx, solver_id, api_url):
    """Get solver status by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        click.echo(json.dumps(client.get_solver_status(solver_id), indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get solver status: {e}", err=True)
        raise click.Abort()
