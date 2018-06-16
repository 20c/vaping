
import os
import pytest


@pytest.fixture
def this_dir():
    return os.path.dirname(__file__)


pytest.setup_filedata(os.path.dirname(__file__))


def pytest_generate_tests(metafunc):
    for fixture in metafunc.fixturenames:
        if fixture.startswith('data_'):
            data = pytest.get_filedata(fixture)
            metafunc.parametrize(fixture, data.values(), ids=data.keys())
