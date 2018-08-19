
import os
import pytest


@pytest.fixture
def this_dir():
    return os.path.dirname(__file__)


@pytest.fixture
def config_dir():
    return os.path.join(this_dir(), "data", "config")


pytest.setup_filedata(os.path.dirname(__file__))


def pytest_generate_tests(metafunc):
    for fixture in metafunc.fixturenames:
        if fixture.startswith('data_'):
            data = pytest.get_filedata(fixture)
            metafunc.parametrize(fixture, list(data.values()), ids=list(data.keys()))
