from . import login as _login
from . import auth as _auth
from . import api_keys as _api_keys
from . import simulations as _simulations
from . import projects as _projects
from . import jobs as _jobs
from . import config as _config
from . import scenarios as _scenarios
from . import programs as _programs
from . import devices as _devices
from . import scenes as _scenes
from . import solvers as _solvers

all_commands = [
    _login.login,
    _auth.auth,
    _api_keys.api_keys,
    _simulations.simulations,
    _projects.projects,
    _jobs.jobs,
    _config.config_cmd,
    _scenarios.scenarios,
    _programs.programs,
    _devices.devices,
    _scenes.scenes,
    _solvers.solvers,
]

__all__ = ["all_commands"]
