from __future__ import absolute_import

import vaping
import vaping.config

try:
    import vodka
    import vodka.data
except ImportError:
    pass

try:
    import graphsrv
    import graphsrv.group
except ImportError:
    graphsrv = None



def probe_to_graphsrv(probe):
    """
    takes a probe instance and generates
    a graphsrv data group for it using the
    probe's config
    """

    config = probe.pluginmgr_config

    # manual group set up via `group` config key

    if "group" in config:
        source, group = config["group"].split(".")
        host = config["host"]
        graphsrv.group.add(source, group, {host:{"host":host}}, **config)
        return

    # automatic group setup for fping
    # FIXME: this should be somehow more dynamic

    for k, v in list(config.items()):
        if isinstance(v, dict) and "hosts" in v:
            r = {}
            for host in v.get("hosts"):
                if isinstance(host, dict):
                    r[host["host"]] = host
                else:
                    r[host] = {"host":host}
            graphsrv.group.add(probe.name, k, r, **v)
            break


@vaping.plugin.register('vodka')
class VodkaPlugin(vaping.plugins.EmitBase):

    def init(self):
        self._is_started = False

    def start(self):
        if self._is_started:
            return
        vodka.run(self.pluginmgr_config, self.vaping.config)

        if graphsrv:
            # if graphsrv is installed proceed to generate
            # target configurations for it from probe config

            for node in self.vaping.config.get("probes", []):
                probe = vaping.plugin.get_probe(node, self.vaping)
                probe_to_graphsrv(probe)

        self._is_started = True

    def emit(self, data):
        if not self._is_started:
            self.start()

        vodka.data.handle(data.get("type"), data, data_id=data.get("source"), caller=self)
