"""Tests for the landslide-cli tool using CliRunner."""

from click.testing import CliRunner

from landslide_cli.main import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Landslide platform CLI" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0


def test_login_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["login", "--help"])
    assert result.exit_code == 0
    assert "email" in result.output


def test_auth_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["auth", "--help"])
    assert result.exit_code == 0


def test_api_keys_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["api-keys", "--help"])
    assert result.exit_code == 0


def test_simulations_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["simulations", "--help"])
    assert result.exit_code == 0


def test_projects_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["projects", "--help"])
    assert result.exit_code == 0


def test_jobs_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["jobs", "--help"])
    assert result.exit_code == 0


def test_config_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "--help"])
    assert result.exit_code == 0


def test_config_show():
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0


def test_auth_status_no_api():
    runner = CliRunner()
    result = runner.invoke(cli, ["auth", "status"])
    assert result.exit_code == 0
