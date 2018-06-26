
import os
import pytest
import vaping.plugins.vodka
from vaping import plugin
from vaping.plugins.vodka import probe_to_graphsrv
import graphsrv.group

def test_init(this_dir):
    config_dir = os.path.join(this_dir, 'data', 'config', 'vodka')
    daemon = vaping.daemon.Vaping(config_dir=config_dir)
    vodka = plugin.get_instance("vodka")

def test_probe_to_graphsrv():
    probe = plugin.get_probe({
        "type" : "fping_mtr",
        "name" : "probe_a",
        "host" : "1.1.1.1",
        "interval" : "3s",
        "group" : "a.b"
    }, {})
    probe_to_graphsrv(probe)
    group = graphsrv.group.groups.get("a").get("b")

    assert group["targets"] == {"1.1.1.1":{"host":"1.1.1.1"}}

    probe = plugin.get_probe({
        "type" : "fping",
        "name" : "probe_b",
        "interval" : "3s",
        "dns": {
            "hosts": [{
                "host" : "1.1.1.1",
                "name" : "Cloudflare"
            }]
        }
    }, {})
    probe_to_graphsrv(probe)
    group = graphsrv.group.groups.get("probe_b").get("dns")

    assert group["targets"] == {"1.1.1.1":{"host":"1.1.1.1", "name":"Cloudflare"}}
