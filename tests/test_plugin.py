
import pytest
from vaping import plugin
from vaping import plugins

config = {
    'plugin': [
        {
        'name': 'fancy_probe',
        'type': 'probe0',
        'var0': 24,
        'str0': 'reeb',
        'interval': '5s',
        },
        {
        'name': 'emit0',
        'type': 'emit0',
        'var0': 42,
        'str0': 'beer',
        },
        {
        'name': 'fancy_copy',
        'type': 'fancy_probe',
        'var0': 12345,
        },
    ],
}

anon_config = {
    'type': 'plugin0',
    'var0': 999,
}


@plugin.register('plugin0')
class Plugin0(plugins.PluginBase):
    pass


@plugin.register('emit0')
class EmitPlugin0(plugins.EmitBase):
    def emit(self, msg):
        pass


@plugin.register('emit_abc')
class EmitPluginABC(plugins.EmitBase):
    # emit not defined to test TypeError
    pass


@plugin.register('probe0')
class TimedPlugin0(plugins.TimedProbe):
    default_config = {
        'interval': '1m',
        'count': 5,
        'period': 20,
    }

    def probe(self):
        return []


@plugin.register('probe1')
class ProbePlugin1(plugins.ProbeBase):
    def probe(self):
        return []


def test_plugin_registry():
    assert Plugin0 == plugin.get_plugin_class('plugin0')
    with pytest.raises(ValueError):
        plugin.get_plugin_class('nonexistant')

    with pytest.raises(ValueError):
        @plugin.register('plugin0')
        class p0(plugins.PluginBase):
            pass


def test_plugin_default_config():
    cls = plugin.get_plugin_class("probe0")
    probe = cls({}, None)
    assert probe.pluginmgr_config == cls.default_config


def test_plugin_instance():
    with pytest.raises(ValueError):
        plugin.new_plugin({}, None)

    with pytest.raises(ValueError):
        plugin.get_instance('nonexistant', None)
    with pytest.raises(ValueError):
        plugin.get_instance(['unparsable'], None)

    plugin.instantiate(config['plugin'], None)
    for each in config['plugin']:
        if 'name' not in each:
            continue
        obj = plugin.get_instance(each['name'], None)
        for k,v in list(each.items()):
            assert v == obj.config[k]

    obj = plugin.get_instance(anon_config, None)
    assert obj.config == anon_config

    # copy ctor
    obj = plugin.get_instance('fancy_copy', None)
    assert 'reeb' == obj.config['str0']

    obj = plugin.get_instance({'fancy_copy': {'var0': 'luggage'}}, None)
    assert 'reeb' == obj.config['str0']

    with pytest.raises(TypeError):
        plugin.get_probe('emit0', None)
    assert None != plugin.get_probe('probe1', None)
    assert not hasattr(plugin.get_probe('probe1', None), 'emit')

    with pytest.raises(TypeError):
        plugin.get_output('emit_abc', None)
    with pytest.raises(TypeError):
        plugin.get_output('probe1', None)
    assert None != plugin.get_output('emit0', None)
