
import os
import pytest
import vaping
import vaping.daemon
import vaping.config


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


def test_empty_config_dir(data_dir):
    config_dir = os.path.join(data_dir, 'config', 'empty')

    with pytest.raises(ValueError) as excinfo:
        daemon = vaping.daemon.Vaping(config_dir=config_dir)
    assert 'no plugins specified' in str(excinfo)


def test_empty_config_dict():
    with pytest.raises(ValueError) as excinfo:
        daemon = vaping.daemon.Vaping(config={})
    assert 'config was not specified' in str(excinfo)


def test_empty_config_object():
    with pytest.raises(ValueError) as excinfo:
        daemon = vaping.daemon.Vaping(config=vaping.Config())
    assert 'config was not specified' in str(excinfo)
