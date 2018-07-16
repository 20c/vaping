
import os
import pytest
import munge
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


def test_empty_config_dir(this_dir):
    config_dir = os.path.join(this_dir, "data", "config", "empty")

    with pytest.raises(ValueError) as excinfo:
        vaping.daemon.Vaping(config_dir=config_dir)
    assert 'no plugins specified' in str(excinfo)


def test_empty_config_dict():
    with pytest.raises(ValueError) as excinfo:
        daemon = vaping.daemon.Vaping(config={})
    assert 'config was not specified' in str(excinfo)


def test_empty_config_object():
    with pytest.raises(ValueError) as excinfo:
        vaping.daemon.Vaping(config=vaping.Config())
    assert 'config was not specified' in str(excinfo)


def test_config_object(this_dir):
    config_dir = os.path.join(this_dir, "data", "config", "fping")
    vaping.daemon.Vaping(config=vaping.Config(read=config_dir))


def test_config_dir_not_found():
    with pytest.raises(IOError) as excinfo:
        daemon = vaping.daemon.Vaping(config_dir="does/not/exist")
    assert 'config dir not found' in str(excinfo)


def test_load_config_files(data_config_daemon):
    codec = munge.get_codec('yaml')()
    data = codec.loads(data_config_daemon.yml)
    data['vaping'] = dict(home_dir=os.path.realpath(data_config_daemon.path))
    daemon = vaping.daemon.Vaping(config=data)
    # print(data_config_daemon.dumps(daemon.config.data))
    data_config_daemon.expected["vaping"]["home_dir"] = os.path.realpath(data_config_daemon.expected["vaping"]["home_dir"])
    assert data_config_daemon.expected == daemon.config.data


def test_start_stop(this_dir):
    config_dir = os.path.join(this_dir, "data", "config", "fping")
    daemon = vaping.daemon.Vaping(config=vaping.Config(read=config_dir))
#    daemon._main()
#    daemon.stop()
