import json

import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="scenarios", help="Manage scenarios.")
def scenarios():
    pass


@scenarios.command(name="list")
@click.option("--limit", "-l", type=int, default=20, help="Max results")
@click.option("--tags", "-t", default=None, help="Filter by comma-separated tags")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_scenarios(ctx, limit, tags, api_url):
    """List scenarios."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_scenarios(limit=limit, tags=tags)
        scenarios_list = result if isinstance(result, list) else result.get("scenarios", result.get("items", []))
        if not scenarios_list:
            click.echo("No scenarios found.")
            return
        rows = []
        for s in scenarios_list:
            rows.append([
                s.get("id", "")[:12],
                s.get("name", ""),
                s.get("status", ""),
                ", ".join(s.get("domains", [])),
            ])
        click.echo(tabulate(rows, headers=["ID", "Name", "Status", "Domains"]))
    except Exception as e:
        click.echo(f"Failed to list scenarios: {e}", err=True)
        raise click.Abort()


@scenarios.command(name="create")
@click.option("--name", "-n", required=True, help="Scenario name")
@click.option("--description", "-d", default="", help="Description")
@click.option("--domains", required=True, help="Comma-separated domains")
@click.option("--mc-runs", type=int, default=100, help="Monte Carlo runs")
@click.option("--horizon", type=int, default=100, help="Time horizon steps")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def create_scenario(ctx, name, description, domains, mc_runs, horizon, api_url):
    """Create a new scenario."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {
        "name": name,
        "description": description,
        "domains": [d.strip() for d in domains.split(",")],
        "mc_runs": mc_runs,
        "horizon": horizon,
    }
    try:
        result = client.create_scenario(data)
        click.echo(f"Scenario created: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to create scenario: {e}", err=True)
        raise click.Abort()


@scenarios.command(name="get")
@click.argument("scenario-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def get_scenario(ctx, scenario_id, api_url):
    """Get scenario details by ID."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        scenario = client.get_scenario(scenario_id)
        click.echo(json.dumps(scenario, indent=2, default=str))
    except Exception as e:
        click.echo(f"Failed to get scenario: {e}", err=True)
        raise click.Abort()


@scenarios.command(name="fork")
@click.argument("scenario-id")
@click.option("--name", "-n", required=True, help="New scenario name")
@click.option("--description", "-d", default="", help="New description")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def fork_scenario(ctx, scenario_id, name, description, api_url):
    """Fork an existing scenario."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {"name": name}
    if description:
        data["description"] = description
    try:
        result = client.fork_scenario(scenario_id, data)
        click.echo(f"Scenario forked: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to fork scenario: {e}", err=True)
        raise click.Abort()
