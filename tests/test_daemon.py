
import pytest
import vaping
import vaping.daemon


def test_init():
    pass


def test_plugin_context():
    data = {
        '1': 'two'
        }
    cfg = vaping.Config(data=data)
    ctx = vaping.daemon.PluginContext(cfg)
    assert data == ctx.config.data

    # test immutable
    ctx.config.data['1'] = 'three'
    assert data != ctx.config.data

