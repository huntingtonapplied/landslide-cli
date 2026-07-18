import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

CONFIG_DIR = Path.home() / ".landslide"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "auth_mode": "api_key",
    "default_project": None,
    "timeout": 30,
    "max_retries": 3,
}


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
