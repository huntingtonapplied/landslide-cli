import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

CONFIG_DIR = Path.home() / ".landslide"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

# Production API base. A fresh download with no config/key must reach prod, not a
# localhost dev port. The client prepends /v1 to every path, so the base is the
# bare host (no /v1 suffix — avoids a double prefix).
DEFAULT_API_URL = "https://api.landslide.global"

DEFAULT_CONFIG = {
    "api_url": DEFAULT_API_URL,
    "auth_mode": "api_key",
    "default_project": None,
    "timeout": 30,
    "max_retries": 3,
}


def get_api_url(override=None):
    """Resolve the API base URL through one place.

    Precedence: explicit override (e.g. --api-url flag) > LANDSLIDE_API_URL env
    var > ~/.landslide/config.yaml > prod default. Dev overrides are preserved;
    only the built-in default changed from localhost to prod.
    """
    if override:
        return override
    env = os.environ.get("LANDSLIDE_API_URL")
    if env:
        return env
    return load_config().get("api_url", DEFAULT_API_URL)


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    if not CONFIG_PATH.exists():
        return dict(DEFAULT_CONFIG)
    if yaml is None:
        raise ImportError("PyYAML is required to read config files")
    with open(CONFIG_PATH) as f:
        return {**DEFAULT_CONFIG, **yaml.safe_load(f)}


def save_config(config):
    if yaml is None:
        raise ImportError("PyYAML is required to write config files")
    ensure_config_dir()
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    CONFIG_PATH.chmod(0o600)  # creds file: owner-only (was world-readable; boltzmann parity)


def get_api_key():
    config = load_config()
    return config.get("api_key") or os.environ.get("LANDSLIDE_API_KEY")


def get_auth_token():
    config = load_config()
    return config.get("auth_token") or os.environ.get("LANDSLIDE_AUTH_TOKEN")


KNOWN_CONFIG_KEYS = {
    "api_url",
    "auth_mode",
    "default_project",
    "timeout",
    "max_retries",
    "api_key",
    "auth_token",
    "last_update_check",
}


def validate_config(config):
    """Return a list of warning messages for invalid config entries."""
    warnings = []
    for key in config:
        if key not in KNOWN_CONFIG_KEYS:
            from difflib import get_close_matches

            matches = get_close_matches(key, KNOWN_CONFIG_KEYS, n=1, cutoff=0.5)
            msg = f"Unknown config key: '{key}'"
            if matches:
                msg += f" (did you mean '{matches[0]}'?)"
            warnings.append(msg)
    if "api_url" in config:
        url = config["api_url"]
        if isinstance(url, str) and not (url.startswith("http://") or url.startswith("https://")):
            warnings.append("api_url should start with http:// or https://")
    return warnings
