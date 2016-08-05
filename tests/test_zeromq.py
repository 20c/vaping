
import pytest
import vaping.plugins.zeromq


def test_init():
    obj = vaping.plugins.zeromq.ZeroMQ({}, None)
    assert obj.skip == True

    obj = vaping.plugins.zeromq.ZeroMQ({'bind': 'tcp://*:5555'}, None)
    assert obj.skip == False

