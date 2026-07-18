import click

from ..config import CONFIG_PATH, load_config


@click.command(name="config")
@click.argument("action", type=click.Choice(["show", "validate"]))
@click.pass_context
def config_cmd(ctx, action):
    """Manage CLI configuration (~/.landslide/config.yaml).

    Actions: show, validate
    """
    if action == "show":
        config = load_config()
        click.echo(f"Config file: {CONFIG_PATH}")
        for k, v in config.items():
            masked = k.endswith("token") or k.endswith("key")
            click.echo(f"  {k}: {'***' if masked else v}")
    elif action == "validate":
        config = load_config()
        issues = []
        if not config.get("api_url"):
            issues.append("api_url is not set")
        if not config.get("auth_token") and not config.get("api_key"):
            issues.append("No auth_token or api_key found - run 'landslide login'")
        if issues:
            click.echo("Configuration issues:")
            for issue in issues:
                click.echo(f"  - {issue}")
        else:
            click.echo("Configuration looks valid.")
