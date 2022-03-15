import logging

from prometheus_client import REGISTRY

import vaping

logging.basicConfig(level=logging.DEBUG)


def test_include():
    cls = vaping.plugin.get_plugin_class("prometheus")

    config = dict(
        port=12345,
    )
    prom = cls(config, None)

    emit_data = dict(
        data=[
            dict(
                host="host0",
                min=1.2,
                max=2.5,
                avg=1.6,
                cnt=5,
                loss=1.0,
            )
        ]
    )

    # need to find where this gets put in the registry
    before = REGISTRY.get_sample_value("number_of_packets_sent")
    prom.emit(emit_data)
    """
    after =  REGISTRY.get_sample_value('number_of_packets_sent')
    pkts = REGISTRY.get_sample_value('sent_packets_total')
    pkts = REGISTRY.get_sample_value('number_of_packets_sent_total')
    print(REGISTRY._get_names())
    assert pkts
    assert after > before
    """
