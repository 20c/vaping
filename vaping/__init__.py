from __future__ import absolute_import

# import to namespace
from .config import Config # noqa
from pluginmgr.config import ConfigPluginManager


class PluginManager(ConfigPluginManager):
    def get_probe(self, node, pctx):
        obj = self.get_instance(node, pctx)
        if not hasattr(obj, 'probe'):
            raise TypeError('%s is not a probe plugin, missing ::probe()' % (obj.name))
        return obj

    def get_output(self, node, pctx):
        obj = self.get_instance(node, pctx)
        if not hasattr(obj, 'emit'):
            name = obj.pluginmgr_config.get('name', str(node))
            raise TypeError('%s is not an output plugin, missing ::emit()' % (name))
        return obj


plugin = PluginManager('vaping.plugins')
