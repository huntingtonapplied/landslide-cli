import json

import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="jobs", help="Manage job executions.")
def jobs():
    pass


@jobs.command(name="list")
@click.option("--status", "-s", default=None, help="Filter by status")
@click.option("--limit", "-l", type=int, default=20, help="Max results")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_jobs(ctx, status, limit, api_url):
    """List job executions."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_executions(limit=limit, status=status)
        execs = result if isinstance(result, list) else result.get("executions", result.get("items", []))
        if not execs:
            click.echo("No jobs found.")
            return
        rows = []
        for e in execs:
            rows.append([
                e.get("id", "")[:12],
                e.get("scenario_id", "")[:12],
                e.get("status", ""),
                e.get("created_at", ""),
            ])
        click.echo(tabulate(rows, headers=["Job ID", "Scenario", "Status", "Created"]))
    except Exception as e:
        click.echo(f"Failed to list jobs: {e}", err=True)
        raise click.Abort()


@jobs.command(name="status")
@click.argument("job-id")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def job_status(ctx, job_id, api_url):
    """Get job execution status and results."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.get_execution_status(job_id)
        click.echo(json.dumps(result, indent=2, default=str))
    except Exception:
        try:
            result = client.get_execution(job_id)
            click.echo(json.dumps(result, indent=2, default=str))
        except Exception as e:
            click.echo(f"Failed to get job status: {e}", err=True)
            raise click.Abort()
