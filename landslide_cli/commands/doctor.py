"""landslide doctor — no-key connectivity/config check.

Pings the resolved (production by default) API base and reports whether it is
reachable and whether credentials are present, so a fresh download with no key
can confirm it is talking to prod (and just needs to log in) rather than
silently failing against a localhost dev port.
"""

import os
import sys

import click
import httpx

from landslide_cli import __version__
from landslide_cli.config import (
    CONFIG_PATH,
    get_api_key,
    get_api_url,
    get_auth_token,
    load_config,
    validate_config,
)
from landslide_cli.log import logger
from landslide_cli.output import is_json, print_json


def _check(label, ok, detail="", json_mode=False):
    """Print a check result and return it as a dict."""
    result = {"check": label, "ok": ok}
    if detail:
        result["detail"] = detail
    if not json_mode:
        icon = "✓" if ok else "✗"
        msg = f"  {icon} {label}"
        if detail:
            msg += f"  ({detail})"
        click.echo(msg, err=not ok)
    return result


@click.command(name="doctor")
@click.option("--api-url", envvar="LANDSLIDE_API_URL", help="API base URL")
@click.pass_context
def doctor(ctx, api_url):
    """Check your Landslide CLI setup and connectivity."""
    json_mode = is_json(ctx)
    results = []

    if not json_mode:
        click.echo(f"Landslide CLI v{__version__}")
        click.echo()

    # 1. Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 8)
    results.append(_check("Python >= 3.8", py_ok, py_ver, json_mode))

    # 2. Config file exists (optional — defaults apply without it)
    config_exists = CONFIG_PATH.exists()
    results.append(
        _check(
            "Config file exists",
            config_exists,
            str(CONFIG_PATH) if config_exists else "using built-in defaults",
            json_mode,
        )
    )

    # 3. Config is valid
    config = load_config()
    config_warnings = validate_config(config) if config else []
    config_valid = len(config_warnings) == 0
    detail = "; ".join(config_warnings) if config_warnings else "ok"
    results.append(_check("Config is valid", config_valid, detail, json_mode))

    # 4. Resolved API URL (shows which host we will actually hit)
    resolved_url = get_api_url(api_url)
    source = "flag/env" if (api_url or os.environ.get("LANDSLIDE_API_URL")) else (
        "config file" if config_exists else "default (prod)"
    )
    results.append(_check("API URL resolved", True, f"{resolved_url} [{source}]", json_mode))

    # 5. API reachable (unauthenticated /health ping)
    api_reachable = False
    reach_detail = resolved_url
    try:
        resp = httpx.get(
            f"{resolved_url.rstrip('/')}/health",
            timeout=5.0,
            follow_redirects=True,
        )
        api_reachable = resp.status_code < 500
        reach_detail = f"{resolved_url} (HTTP {resp.status_code})"
    except Exception as e:
        logger.debug("API health check failed: %s", e)
        reach_detail = f"{resolved_url} (unreachable: {type(e).__name__})"
    results.append(_check("API reachable", api_reachable, reach_detail, json_mode))

    # 6. Credentials present (auth token or API key)
    token = get_auth_token()
    api_key = get_api_key()
    has_creds = bool(token or api_key)
    if token:
        cred_src = "auth token"
    elif api_key:
        cred_src = "api key"
    else:
        cred_src = "none — run 'landslide login'"
    results.append(_check("Credentials present", has_creds, cred_src, json_mode))

    # 7. Auth status against the resolved host (only if reachable + creds)
    auth_ok = False
    auth_detail = "skipped"
    if api_reachable:
        if has_creds:
            try:
                from landslide_cli.client import LandslideClient

                client = LandslideClient(api_url=resolved_url)
                status = client.get_auth_status()
                auth_ok = bool(
                    status.get("authenticated", status.get("healthy", False))
                )
                auth_detail = "verified" if auth_ok else "credentials rejected"
            except Exception as e:
                logger.debug("Auth check failed: %s", e)
                auth_detail = "could not verify"
        else:
            auth_detail = "not logged in"
    results.append(_check("Authenticated", auth_ok, auth_detail, json_mode))

    all_ok = all(r["ok"] for r in results)

    if json_mode:
        print_json({"ok": all_ok, "api_url": resolved_url, "checks": results})
    else:
        click.echo()
        if all_ok:
            click.echo("All checks passed.")
        elif api_reachable and not has_creds:
            click.echo(
                f"Reached {resolved_url} but you are not logged in. "
                "Run 'landslide login' to authenticate."
            )
        else:
            click.echo("Some checks failed. See details above.", err=True)
