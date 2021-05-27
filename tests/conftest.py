import os

import pytest
import pytest_filedata

pytest_filedata.setup(os.path.dirname(__file__))


def _this_dir():
    """
    returns dirname for location of this file

    py.test no longer allows fixtures to be called
    directly so we provide a private function
    instead that can be
    """
    return os.path.dirname(__file__)


@pytest.fixture
def this_dir():
    return _this_dir()


@pytest.fixture
def config_dir():
    return os.path.join(_this_dir(), "data", "config")


@pytest.fixture
def schema_dir():
    return os.path.join(_this_dir(), "data", "schema")


def pytest_generate_tests(metafunc):
    for fixture in metafunc.fixturenames:
        if fixture.startswith("data_"):
            data = pytest_filedata.get_data(fixture)
            metafunc.parametrize(fixture, list(data.values()), ids=list(data.keys()))
