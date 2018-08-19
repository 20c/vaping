from __future__ import absolute_import

# import to namespace
from vaping.config import Config
from pluginmgr.config import ConfigPluginManager


def check_method(obj, method, node):
    if not hasattr(obj, method):
        name = obj.config.get('name', str(node))
        raise TypeError("plugin type mismatch, {} is missing ::{}()".format(name, method))


class PluginManager(ConfigPluginManager):
    def exists(self, name):
        if name in self._instance:
            return True
        return False

    def get_probe(self, node, pctx):
        obj = self.get_instance(node, pctx)
        check_method(obj, "probe", node)
        return obj

    def get_output(self, node, pctx):
        obj = self.get_instance(node, pctx)
        check_method(obj, "emit", node)
        return obj


plugin = PluginManager('vaping.plugins')
