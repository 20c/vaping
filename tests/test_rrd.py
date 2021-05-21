import pytest
import vaping.plugins.rrd


def test_valid_schema():
    config = {
        "name": "rrd_avg",
        "type": "rrd",
        "field": "avg",
        "filename": "{source}-{host}-{field}.rrd",
        "step": 3,
        "data_sources": ["DS:latency:GAUGE:4:0:U"],
        "archives": ["RRA:AVERAGE:0.5:1:1000"]

    }
    rrd = vaping.plugin.get_plugin_class("rrd")(config, None)

    # Assert config is loaded into rrd config
    for k,v in config.items():
        assert rrd.config[k] == v

    # Assert certain values are available as attributes of rrd plugin

    assert rrd.data_sources == config["data_sources"]
    assert rrd.step == config["step"]
    assert rrd.archives == config["archives"]
