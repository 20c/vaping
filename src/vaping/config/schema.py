import confu.exceptions
import confu.generator
import confu.schema


class MixedDict(confu.schema.Dict):
    """
    Extended confu.schema.Dict object that prevents
    validation of its interior objects.
    Use for dictionaries that do not need validation or
    will get validated other ways, like in Vodka plugin or logging.
    """

    def validate(self, config, path=None, errors=None, warnings=None):
        return config


class HostSchema(confu.schema.Schema):
    # host = confu.schema.IpAddress()
    # FPing just needs a string here
    host = confu.schema.Str()
    name = confu.schema.Str()
    color = confu.schema.Str()


class GroupSchema(confu.schema.Schema):
    name = confu.schema.Str()
    hosts = confu.schema.List(item=HostSchema(), help="list of hosts")


class ProbesSchema(confu.schema.Schema):
    """
    Configuration schema for probes
    """

    name = confu.schema.Str()
    type = confu.schema.Str()
    output = confu.schema.List(item=confu.schema.Str(), help="list of outputs")
    groups = confu.schema.List(item=GroupSchema(), help="group schema")


class PluginProxySchema(confu.schema.ProxySchema):
    """
    Will properly route plugin validation to the correct
    plugin schema
    """

    def schema(self, config):
        import vaping

        try:
            return vaping.plugin.get_plugin_class(config["type"]).ConfigSchema()
        except KeyError:
            raise ValueError("All plugins need `type` field set in config.")

    def validate(self, config, path=None, errors=None, warnings=None):
        try:
            path[-1] = config["name"]
        except KeyError:
            raise ValueError("All plugins need `name` field set in config.")

        return self.schema(config).validate(
            config, path=path, errors=errors, warnings=warnings
        )


class VapingSchema(confu.schema.Schema):
    """
    Configuration schema for vaping config
    """

    plugin_path = confu.schema.List(
        item=confu.schema.Directory(),
        help="list of directories to search for plugins",
    )

    probes = confu.schema.List(item=ProbesSchema(), help="list of probes")

    plugins = confu.schema.List(
        item=PluginProxySchema(), help="list of plugin config objects"
    )

    # config_dir = confu.schema.Directory(default="~/.vaping")
    config_dir = confu.schema.Directory(default="")
    home_dir = confu.schema.Directory(default=None)
    pidfile = confu.schema.Str(default="vaping.pid")
