"""Landslide CLI entry point."""

import os
import signal
import sys

import click

from landslide_cli import __version__
from landslide_cli.commands import all_commands
from landslide_cli.config import load_config, validate_config
from landslide_cli.exit_codes import EXIT_GENERAL, EXIT_SIGINT, EXIT_SIGTERM
from landslide_cli.log import setup_logging, logger
from landslide_cli.update_check import UpdateChecker


@click.group(context_settings=dict(help_option_names=["-h", "--help"], show_default=True))
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="Landslide API URL")
@click.option("--timeout", type=int, default=30, help="Request timeout in seconds")
@click.option("--output", "-o", type=click.Choice(["table", "json", "yaml"]), default="table",
              help="Output format (default: table)")
@click.option("--no-color", is_flag=True, default=False, envvar="NO_COLOR",
              help="Disable colored output")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Show informational messages (INFO level)")
@click.option("--debug", is_flag=True, default=False,
              help="Show debug messages including HTTP requests")
@click.option("--ci", is_flag=True, default=False,
              help="CI mode: no color, no spinners, no interactive prompts")
@click.version_option(version=__version__, prog_name="landslide")
@click.pass_context
def cli(ctx, api_url, timeout, output, no_color, verbose, debug, ci):
    """Landslide platform CLI - interact with the Landslide REST API.

    Manage simulations, projects, jobs, API keys, and authentication
    for the Landslide simulation platform.
    """
    # Auto-detect CI environment
    if not ci and (os.getenv("CI") or os.getenv("GITHUB_ACTIONS") or os.getenv("GITLAB_CI")):
        ci = True
    if ci:
        no_color = True

    ctx.ensure_object(dict)
    ctx.obj["api_url"] = api_url
    ctx.obj["timeout"] = timeout
    ctx.obj["output"] = output
    ctx.obj["no_color"] = no_color
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["ci"] = ci
    setup_logging(verbose=verbose, debug=debug)

    # Validate config and warn about issues (non-fatal)
    try:
        config = load_config()
        if config:
            for w in validate_config(config):
                click.echo(f"Warning: {w}", err=True)
    except Exception as e:
        logger.debug("Config validation skipped: %s", e)


for cmd in all_commands:
    cli.add_command(cmd)


_update_checker = UpdateChecker()


def main():
    """Entry point with top-level signal and exception handling."""
    signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(EXIT_SIGTERM))
    _update_checker.start()
    try:
        cli(standalone_mode=False)
    except click.exceptions.Exit as e:
        raise SystemExit(e.exit_code)
    except (KeyboardInterrupt, click.Abort):
        raise SystemExit(EXIT_SIGINT)
    except SystemExit:
        raise
    except click.ClickException as e:
        e.show()
        raise SystemExit(e.exit_code)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise SystemExit(EXIT_GENERAL)
    finally:
        _update_checker.notify_if_outdated()


if __name__ == "__main__":
    main()
