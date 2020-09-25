import confu.schema
import confu.generator
import confu.exceptions


class HostSchema(confu.schema.Schema):
    host = confu.schema.IpAddress()
    name = confu.schema.Str()
    color = confu.schema.Str()


class GroupSchema(confu.schema.Schema):
    name = confu.schema.Str()
    hosts = confu.schema.List(
        item=HostSchema(), help="list of hosts"
    )


class ProbesSchema(confu.schema.Schema):
    """
    Configuration schema for probes
    """
    name = confu.schema.Str()
    type = confu.schema.Str()
    output = confu.schema.List(
        item=confu.schema.Str(), help="list of outputs"
    )
    groups = confu.schema.List(
        item=GroupSchema(), help="group schema"
    )


class PluginProxySchema(confu.schema.ProxySchema):
    """
    Will properly route plugin validation to the correct
    plugin schema
    """

    def schema(self, config):
        import vaping
        
        return vaping.plugin.get_plugin_class(config["type"]).ConfigSchema()

    def validate(self, config, path=None, errors=None, warnings=None):
        path[-1] = config["name"]
        return self.schema(config).validate(
            config, path=path, errors=errors, warnings=warnings
        )

class VapingSchema(confu.schema.Schema):
    """
    Configuration schema for vaping config
    """

    plugin_path = confu.schema.List(
        item=confu.schema.Directory("plugin_path.item"),
        help="list of directories to search for plugins",
    )

    probes = confu.schema.List(
        item=ProbesSchema(), help="list of probes"
    )

    plugins = confu.schema.List(
        item=PluginProxySchema(), help="list of plugin config objects"
    )

