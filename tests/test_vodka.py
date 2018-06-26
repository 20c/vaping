
import os
import pytest
import vaping.plugins.vodka
from vaping import plugin


def test_init(this_dir):
    config_dir = os.path.join(this_dir, 'data', 'config', 'vodka')
    daemon = vaping.daemon.Vaping(config_dir=config_dir)
    vodka = plugin.get_instance("vodka")
