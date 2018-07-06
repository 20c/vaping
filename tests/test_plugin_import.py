
import logging

import vaping

logging.basicConfig(level=logging.DEBUG)


def test_include():
    vaping.plugin.get_plugin_class('zeromq')
#    inst = cls()
#    assert None != inst

