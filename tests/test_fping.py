
import os
import pytest
import vaping.plugins.fping
from vaping import plugin


expect_verbose = {
    '10.130.133.1 : 273.89 298.10 322.58': {
        'host': '10.130.133.1',
        'min': 273.89,
        'max': 322.58,
        'avg': 298.19,
        'cnt': 3,
        'loss': 0.0,
        'last': 322.58,
        },
    '10.130.133.2 : 100 - 50': {
        'host': '10.130.133.2',
        'min': 50.0,
        'max': 100.0,
        'avg': 75.0,
        'cnt': 3,
        'loss': 0.333,
        'last': 50,
        },
    '10.130.133.2 : - - -': {
        'host': '10.130.133.2',
        'cnt': 3,
        'loss': 1,
        },
    'example.com: Temporary failure in name resolution': {
        }
    }


def test_parse_verbose():
    fping = vaping.plugins.fping.FPing({'interval': '5s'}, None)
    for line, expected in list(expect_verbose.items()):
        res = fping.parse_verbose(line)
        for k,v in list(expected.items()):
            if isinstance(v, float):
                assert abs(v - res[k]) < 0.001
            else:
                assert v == res[k]


def test_run_probe(this_dir):
    config_dir = os.path.join(this_dir, 'data', 'config', 'fping')
    daemon = vaping.daemon.Vaping(config_dir=config_dir)
    probes = daemon.config.get('probes', None)

    fping = plugin.get_probe(probes[0], daemon.plugin_context)
    msg = fping.probe()
    print(msg)
