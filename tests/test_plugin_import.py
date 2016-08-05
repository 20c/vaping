
import pytest

import vaping

import logging
logging.basicConfig(level=logging.DEBUG)


def test_include():

    cls = vaping.plugin.get_plugin_class('zeromq')
#    inst = cls()
#    assert None != inst

