
import pytest
from vaping.config import parse_interval


def test_parse_interval():
    assert 1 == parse_interval('1s')
    assert .5 == parse_interval('500ms')
    assert 300 == parse_interval('5m')
    assert 3600 == parse_interval('1h')
    assert 86400 == parse_interval('1d')

    with pytest.raises(ValueError):
        parse_interval('1x')

