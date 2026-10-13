import ssl
import time
from urllib.parse import urljoin

import click
import httpx

from .config import get_api_key, get_api_url, get_auth_token, load_config


class LandslideClient:
    def __init__(self, api_url=None, timeout=None, max_retries=None):
        config = load_config()
        self.api_url = get_api_url(api_url).rstrip("/")
        self.timeout = timeout or config["timeout"]
        self.max_retries = max_retries or config["max_retries"]
        # httpx (not requests): requests drags in certifi, whose importlib.resources
        # loader raises a bare ImportError under Nuitka onefile — it broke this CLI's
        # published binary at import time. httpx matches the fleet's other CLIs
        # (tillio/slai) and imports cleanly. follow_redirects=True keeps requests'
        # default redirect behaviour (avoids 307 -> JSON-parse bugs).
        #
        # verify=<system SSLContext> builds the trust store from the OS rather than
        # certifi. NOTE: this does NOT by itself fix the compiled-binary network
        # crash — httpcore's _ssl module imports certifi unconditionally at import
        # time, and certifi/core.py's `from importlib.resources import as_file,
        # files` raises a bare ImportError under Nuitka onefile 2.5.9 (fleet-wide:
        # landslide/tillio/slai all fail on real network commands while --version/
        # --help pass). That Nuitka+certifi/importlib.resources issue is tracked
        # separately; using the OS trust store here is still the right default.
        self._session = httpx.Client(
            follow_redirects=True, verify=ssl.create_default_context()
        )

    def _headers(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        token = get_auth_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            api_key = get_api_key()
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _request(self, method, path, **kwargs):
        url = urljoin(self.api_url + "/", path.lstrip("/"))
        headers = self._headers()
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        last_exc = None
        for attempt in range(self.max_retries):
            try:
                resp = self._session.request(
                    method, url, headers=headers, timeout=self.timeout, **kwargs
                )
                if resp.status_code >= 500 and attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                # Actionable auth error instead of a raw httpx 401 (matches the
                # fleet CLIs' "run login" hint — HQ2 B3.3). Raising a ClickException
                # (not an httpx error) surfaces cleanly via main's handler AND skips
                # the httpx.HTTPError retry loop below, so a 401 fails fast.
                if resp.status_code == 401:
                    raise click.ClickException(
                        "Not authenticated (401).\n"
                        "  Run: landslide login\n"
                        "  Or set LANDSLIDE_API_KEY (see: landslide doctor)."
                    )
                resp.raise_for_status()
                return resp.json() if resp.text else None
            except httpx.HTTPError as e:
                last_exc = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise

        raise last_exc

    def _get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def _post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def _put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def _patch(self, path, **kwargs):
        return self._request("PATCH", path, **kwargs)

    def _delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)

    # Health (unauthenticated, top-level — NOT under /v1)
    def health(self):
        return self._get("/health")

    # Auth endpoints
    def login(self, email, password):
        return self._post("/v1/auth/login", json={"username": email, "password": password})

    def get_auth_status(self):
        return self._get("/v1/auth/health")

    # API keys
    def list_api_keys(self):
        return self._get("/v1/users/me/api-keys")

    def create_api_key(self, name, permissions=None):
        payload = {"name": name}
        if permissions:
            payload["permissions"] = permissions
        return self._post("/v1/users/me/api-keys", json=payload)

    def rotate_api_key(self, key_id):
        return self._post(f"/v1/users/me/api-keys/{key_id}/regenerate")

    def update_api_key(self, key_id, data):
        return self._patch(f"/v1/users/me/api-keys/{key_id}", json=data)

    def revoke_api_key(self, key_id):
        return self._delete(f"/v1/users/me/api-keys/{key_id}")

    def get_api_key_stats(self):
        return {"error": "Not available"}

    # Simulations
    def list_simulations(self, status_filter=None, limit=None):
        params = {}
        if status_filter:
            params["status_filter"] = status_filter
        if limit:
            params["limit"] = limit
        return self._get("/v1/simulations", params=params)

    def get_simulation(self, sim_id):
        return self._get(f"/v1/simulations/{sim_id}")

    def create_simulation(self, data):
        return self._post("/v1/simulations", json={"simulation": data})

    def stop_simulation(self, sim_id):
        return self._post(f"/v1/engine/simulations/{sim_id}/stop")

    # Scenarios
    def list_scenarios(self, limit=None, tags=None):
        params = {}
        if limit:
            params["limit"] = limit
        if tags:
            params["tags"] = tags
        return self._get("/v1/scenarios", params=params)

    def get_scenario(self, scenario_id):
        return self._get(f"/v1/scenarios/{scenario_id}")

    def create_scenario(self, data):
        return self._post("/v1/scenarios", json={"scenario": data})

    def fork_scenario(self, scenario_id, data=None):
        payload = data or {}
        return self._post(f"/v1/scenarios/{scenario_id}/fork", json=payload)

    # Projects
    def list_projects(self, public=None):
        params = {}
        if public:
            params["public"] = public
        return self._get("/v1/projects", params=params)

    def get_project(self, project_id):
        return self._get(f"/v1/projects/{project_id}")

    def create_project(self, data):
        return self._post("/v1/projects", json=data)

    # Programs
    def list_programs(self, limit=None):
        params = {}
        if limit:
            params["limit"] = limit
        return self._get("/v1/programs", params=params)

    def get_program(self, program_id):
        return self._get(f"/v1/programs/{program_id}")

    def create_program(self, data):
        return self._post("/v1/programs", json={"program": data})

    def update_program(self, program_id, data):
        return self._put(f"/v1/programs/{program_id}", json=data)

    def delete_program(self, program_id):
        return self._delete(f"/v1/programs/{program_id}")

    # Devices
    def list_devices(self, limit=None, status=None):
        params = {}
        if limit:
            params["limit"] = limit
        if status:
            params["status"] = status
        return self._get("/v1/devices", params=params)

    def get_device(self, device_id):
        return self._get(f"/v1/devices/{device_id}")

    def create_device(self, data):
        return self._post("/v1/devices", json={"device": data})

    def register_device(self, data):
        return self._post("/v1/devices/register", json=data)

    def get_device_status(self, device_id):
        return self._get(f"/v1/devices/{device_id}/status")

    # Scenes
    def list_scenes(self, limit=None):
        params = {}
        if limit:
            params["limit"] = limit
        return self._get("/v1/scenes", params=params)

    def get_scene(self, scene_id):
        return self._get(f"/v1/scenes/{scene_id}")

    def create_scene(self, data):
        return self._post("/v1/scenes", json={"scene": data})

    def update_scene(self, scene_id, data):
        return self._put(f"/v1/scenes/{scene_id}", json=data)

    # Solvers
    def list_solvers(self, limit=None, domain=None):
        params = {}
        if limit:
            params["limit"] = limit
        if domain:
            params["domain"] = domain
        return self._get("/v1/solvers", params=params)

    def get_solver(self, solver_id):
        return self._get(f"/v1/solvers/{solver_id}")

    def configure_solver(self, solver_id, config):
        return self._post(f"/v1/solvers/{solver_id}/configure", json=config)

    def get_solver_status(self, solver_id):
        return self._get(f"/v1/solvers/{solver_id}/status")

    # Executions / Jobs
    def list_executions(self, limit=None, status=None):
        params = {}
        if limit:
            params["limit"] = limit
        if status:
            params["status"] = status
        return self._get("/v1/executions", params=params)

    def get_execution(self, execution_id):
        return self._get(f"/v1/executions/{execution_id}")

    def get_execution_status(self, execution_id):
        return self._get(f"/v1/executions/{execution_id}/status")
