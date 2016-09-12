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


@vaping.plugin.register('vodka')
class VodkaPlugin(vaping.plugins.EmitBase):

    def init(self):
        self._is_started = False

    def start(self):
        vodka.run(self.config, self.vaping.config)

        if graphsrv:
            # if graphsrv is installed proceed to generate
            # target configurations for it from probe config

            # valid probe types to setup targets for
            valid_types = [
                vaping.plugins.fping.FPing
            ]
            for node in self.vaping.config.get("probes", []):
                probe = vaping.plugin.get_probe(node, self.vaping)
                for typ in valid_types:
                    if isinstance(probe, typ):
                        for k,v in list(probe.config.items()):
                            if isinstance(v, dict) and "hosts" in v:
                                r = {}
                                for host in v.get("hosts"):
                                    if isinstance(host, dict):
                                        r[host["host"]] = host
                                    else:
                                        r[host] = {"host":host}
                                graphsrv.group.add(probe.name, k, r)
                        break

        self._is_started = True

    def emit(self, data):
        if not self._is_started:
            self.start()
        vodka.data.handle(data.get("type"), data, data_id=data.get("source"), caller=self)
