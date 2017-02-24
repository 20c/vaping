
import os
import pytest


@pytest.fixture
def this_dir():
    return os.path.dirname(__file__)


@pytest.fixture
def data_dir():
    return os.path.join(this_dir(), 'data')
