import pytest
import vaping.plugins.zeromq


def test_init():
    with pytest.raises(ValueError):
        vaping.plugins.zeromq.ZeroMQ({}, None)

    config = {
        'bind': 'tcp://*:5555',
        'connect': 'tcp://*:5555',
        }
    with pytest.raises(ValueError):
        vaping.plugins.zeromq.ZeroMQ(config, None)

    vaping.plugins.zeromq.ZeroMQ({'bind': 'tcp://*:5555'}, None)

