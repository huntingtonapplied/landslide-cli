import click
from tabulate import tabulate

from ..client import LandslideClient


@click.group(name="projects", help="Manage projects.")
def projects():
    pass


@projects.command(name="list")
@click.option("--public", is_flag=True, help="Show public projects only")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def list_projects(ctx, public, api_url):
    """List projects."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    try:
        result = client.list_projects(public=public)
        projs = result if isinstance(result, list) else result.get("projects", result.get("items", []))
        if not projs:
            click.echo("No projects found.")
            return
        rows = []
        for p in projs:
            rows.append([
                p.get("id", "")[:12],
                p.get("name", ""),
                p.get("status", ""),
                "public" if p.get("is_public") else "private",
            ])
        click.echo(tabulate(rows, headers=["ID", "Name", "Status", "Visibility"]))
    except Exception as e:
        click.echo(f"Failed to list projects: {e}", err=True)
        raise click.Abort()


@projects.command(name="create")
@click.option("--name", "-n", required=True, help="Project name")
@click.option("--description", "-d", default="", help="Project description")
@click.option("--public", is_flag=True, help="Make project public")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def create_project(ctx, name, description, public, api_url):
    """Create a new project."""
    api_url = api_url or ctx.obj.get("api_url")
    timeout = ctx.obj.get("timeout", 30)
    client = LandslideClient(api_url=api_url, timeout=timeout)
    data = {"name": name, "description": description, "is_public": public}
    try:
        result = client.create_project(data)
        click.echo(f"Project created: {result.get('id', 'N/A')}")
    except Exception as e:
        click.echo(f"Failed to create project: {e}", err=True)
        raise click.Abort()
