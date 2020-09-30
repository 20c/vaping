import os
import pytest
import munge
import vaping
import vaping.daemon
import vaping.config

import confu.config

from pprint import pprint

def test_plugin_context():
    data = {"1": "two"}
    cfg = vaping.Config(data=data)
    ctx = vaping.daemon.PluginContext(cfg)
    assert data == ctx.config.data

    # test immutable
    ctx.config.data["1"] = "three"
    assert data != ctx.config.data


def test_empty_config_file(this_dir):
    config_dir = os.path.join(this_dir, "data", "config", "empty")

    with pytest.raises(ValueError) as excinfo:
        vaping.daemon.Vaping(config_dir=config_dir)
    assert "config was not specified or empty" in str(excinfo.value)


def test_empty_config_dict():
    with pytest.raises(ValueError) as excinfo:
        vaping.daemon.Vaping(config={})
    assert "config was not specified" in str(excinfo.value)


def test_empty_config_object():
    with pytest.raises(ValueError) as excinfo:
        vaping.daemon.Vaping(config=vaping.Config())
    assert "config was not specified" in str(excinfo.value)


def test_config_dir_not_found():
    with pytest.raises(IOError) as excinfo:
        vaping.daemon.Vaping(config_dir="does/not/exist")
    assert "config dir not found" in str(excinfo.value)


def test_load_config_dir(this_dir):
    config_dir = os.path.join(this_dir, "data", "config", "fping")
    daemon = vaping.daemon.Vaping(config_dir=config_dir)
    config = daemon.config
    assert type(config) == confu.config.Config


def test_load_config(this_dir):
    import yaml

    config_path = os.path.join(this_dir, "data", "config", "fping", "config.yml")
    with open(config_path, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            pytest.fail()

    daemon = vaping.daemon.Vaping(config=data)
    config = daemon.config
    assert type(config) == confu.config.Config
