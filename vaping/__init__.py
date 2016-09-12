from __future__ import absolute_import

# import to namespace
from .config import Config # noqa
import pluginmgr


class PluginManager(pluginmgr.PluginManager):
    def get_probe(self, node, pctx):
        obj = self.get_instance(node, pctx)
        if not hasattr(obj, 'probe'):
            raise TypeError('%s is not a probe plugin, missing ::probe()' % (obj.name))
        return obj


    def get_output(self, node, pctx):
        obj = self.get_instance(node, pctx)
        if not hasattr(obj, 'emit'):
            raise TypeError('%s is not an output plugin, missing ::emit()' % (obj.name))
        return obj


plugin = PluginManager('vaping.plugins')

