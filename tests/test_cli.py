from click.testing import CliRunner
from vaping import cli
import pytest


def test_start_no_home():
    runner = CliRunner()
    with pytest.raises(ValueError) as excinfo:
        runner.invoke(cli.cli, ["start"], catch_exceptions=False)

    assert str(excinfo.value).startswith("no config specified")
