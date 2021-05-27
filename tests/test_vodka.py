import asyncio
import os

import graphsrv.group

import vaping.plugins.vodka
from vaping import plugin
from vaping.plugins.vodka import probe_to_graphsrv


def test_init(this_dir):
    config_dir = os.path.join(this_dir, "data", "config", "vodka")
    vaping.daemon.Vaping(config_dir=config_dir)
    plugin.get_instance("vodka")


def test_probe_to_graphsrv():

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # vodka setup with single group plugin

    probe = plugin.get_probe(
        {
            "type": "fping_mtr",
            "name": "probe_a",
            "host": "1.1.1.1",
            "interval": "3s",
            "group": "a.b",
        },
        {},
    )
    probe_to_graphsrv(probe)
    group = graphsrv.group.groups.get("a").get("b")

    assert group["targets"] == {"1.1.1.1": {"host": "1.1.1.1"}}

    # vodka setup with legacy plugin groups (before implementation
    # of #44)
    # TODO: remove with vaping 2.0

    probe = plugin.get_probe(
        {
            "type": "fping",
            "name": "probe_b",
            "interval": "3s",
            "dns": {"hosts": [{"host": "1.1.1.1", "name": "Cloudflare"}]},
        },
        {},
    )
    probe_to_graphsrv(probe)
    group = graphsrv.group.groups.get("probe_b").get("dns")

    assert group["targets"] == {"1.1.1.1": {"host": "1.1.1.1", "name": "Cloudflare"}}

    # vodka setup with plugin group implementation as
    # per #44

    probe = plugin.get_probe(
        {
            "type": "fping",
            "name": "probe_c",
            "interval": "3s",
            "groups": [
                {"name": "dns", "hosts": [{"host": "1.1.1.1", "name": "Cloudflare"}]}
            ],
        },
        {},
    )
    probe_to_graphsrv(probe)
    group = graphsrv.group.groups.get("probe_c").get("dns")

    assert group["targets"] == {"1.1.1.1": {"host": "1.1.1.1", "name": "Cloudflare"}}
