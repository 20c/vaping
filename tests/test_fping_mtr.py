
import os

import vaping.plugins.fping_mtr
from vaping import plugin


expect_verbose = {
    "10.130.133.1 : 273.89 298.10 322.58": {
        "host": "10.130.133.1",
        "min": 273.89,
        "max": 322.58,
        "avg": 298.19,
        "cnt": 3,
        "loss": 0.0,
#        "last" : 302.58,
        },
    "10.130.133.2 : 100 - 50": {
        "host": "10.130.133.2",
        "min": 50.0,
        "max": 100.0,
        "avg": 75.0,
        "cnt": 3,
        "loss": 0.333,
        },
    "10.130.133.2 : - - -": {
        "host": "10.130.133.2",
        "cnt": 3,
        "loss": 1,
        },
    "example.com: Temporary failure in name resolution": {
       }
    }

def assert_parsed(data, parsed):
    # dump in json format for easily adding expected
    print("echo \\\n'{}'\\\n > {}/{}.expected".format(data.dumps(parsed), data.path, data.name))
    assert data.expected == parsed


def test_run_probe(config_dir):
    config_dir = os.path.join(config_dir, "fping_mtr")
    daemon = vaping.daemon.Vaping(config_dir=config_dir)
    probes = daemon.config.get("probes", None)

    mtr = plugin.get_probe(probes[0], daemon.plugin_context)
    msg = mtr.probe()
    print(msg)


def test_parse_traceroute(data_mtr_traceroute):
    mtr = vaping.plugin.get_plugin_class("fping_mtr")({}, None)
    print(data_mtr_traceroute.input)
    print(data_mtr_traceroute.expected)
    print("=======")
    hosts = mtr.parse_traceroute(data_mtr_traceroute.input.splitlines())
    print("HOSTS: {}".format(hosts))
    # XXX need to refactor to properly test if host and hosts not in host
    assert_parsed(data_mtr_traceroute, hosts)
