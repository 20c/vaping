import vaping


def test_valid_schema():
    config = {
        "name": "graphite_avg",
        "type": "graphite",
        "field": "avg",
        "filename": "{source}-{host}-{field}",
        "proto": "https",
        "graphite_host": "0.0.0.0",
        "prefix": "vape",
    }
    graphite = vaping.plugin.get_plugin_class("graphite")(config, None)

    # Assert config is loaded into rrd config
    for k,v in config.items():
        assert graphite.config[k] == v

    # Assert certain values are available as attributes of rrd plugin

    assert graphite.proto == config["proto"]
    assert graphite.graphite_host == config["graphite_host"]
    assert graphite.prefix == config["prefix"]
