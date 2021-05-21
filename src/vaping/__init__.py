# import to namespace
from pluginmgr.config import ConfigPluginManager

from vaping.config import Config  # noqa


def check_method(obj, method, node):
    if not hasattr(obj, method):
        name = obj.config.get("name", str(node))
        raise TypeError(f"plugin type mismatch, {name} is missing ::{method}()")


class PluginManager(ConfigPluginManager):
    """
    Vaping plugin manager

    An instance of this will be instantiated automatically and be available
    as `vaping.plugin`
    """

    def exists(self, name):
        """
        Check if plugin instance exists

        **Arguments**

        - name (`str`): plugin instance name

        **Returns**

        `True` if instance exists, `False` if not
        """

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


plugin = PluginManager("vaping.plugins")
