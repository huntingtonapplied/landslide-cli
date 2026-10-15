import json

import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="simulations", help="Manage simulations.")
def simulations():
    pass


@simulations.command(name="list")
@click.option("--status", "-s", default=None, help="Filter by status")
@click.option("--limit", "-l", type=int, default=20, help="Max results")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_sims(ctx, status, limit, api_url):
    """List simulations."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_simulations(status_filter=status, limit=limit)
        sims = result if isinstance(result, list) else result.get("executions", result.get("simulations", []))
        if not sims:
            click.echo("No simulations found.")
            return
        rows = []
        for s in sims:
            rows.append([
                s.get("id", "")[:12],
                s.get("name", s.get("scenario_name", "")),
                s.get("status", ""),
                s.get("created_at", ""),
            ])
        click.echo(tabulate(rows, headers=["ID", "Name", "Status", "Created"]))
    except Exception as e:
        click.echo(f"Failed to list simulations: {e}", err=True)
        raise click.Abort()


@simulations.command(name="create")
@click.option("--name", "-n", required=True, help="Simulation name")
@click.option("--description", "-d", default="", help="Description")
@click.option("--domains", required=True, help="Comma-separated domains")
@click.option("--mc-runs", type=int, default=100, help="Monte Carlo runs")
@click.option("--horizon", type=int, default=100, help="Time horizon steps")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def create_sim(ctx, name, description, domains, mc_runs, horizon, api_url):
    """Create a new simulation."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {
        "name": name,
        "description": description,
        "domains": [d.strip() for d in domains.split(",")],
        "parameters": {
            "horizonSteps": horizon,
            "mcRuns": mc_runs,
        },
    }
    try:
        result = client.create_simulation(data)
        click.echo(f"Simulation created: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to create simulation: {e}", err=True)
        raise click.Abort()


@simulations.command(name="status")
@click.argument("sim-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def sim_status(ctx, sim_id, api_url):
    """Get simulation status by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        sim = client.get_simulation(sim_id)
        click.echo(json.dumps(sim, indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get simulation: {e}", err=True)
        raise click.Abort()


@simulations.command(name="stop")
@click.argument("sim-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def stop_sim(ctx, sim_id, api_url):
    """Stop a running simulation."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.stop_simulation(sim_id)
        click.echo(f"Simulation {sim_id} stopped.")
    except Exception as e:
        click.echo(f"Failed to stop simulation: {e}", err=True)
        raise click.Abort()
