try:
    import zmq.asyncio as zmq
except ImportError:
    zmq = None

import confu.schema

import vaping
import vaping.plugins


class ZeroMQSchema(vaping.plugins.PluginConfigSchema):
    bind = confu.schema.Str()
    connect = confu.schema.Str()


@vaping.plugin.register("zeromq")
class ZeroMQ(vaping.plugins.EmitBase):
    """
    plugin to emit json encoded messages via zeromq

    # Instanced Attributes

    - ctx (`zmq Context`)
    - sock (`zmq socket`)
    """

    ConfigSchema = ZeroMQSchema

    def __init__(self, config, ctx):
        super().__init__(config, ctx)

        self.sock = None

    def init(self):
        self.log.debug("init zeromq ..")
        if not zmq:
            self.log.critical("missing zeromq, please install pyzmq to use this plugin")
            raise RuntimeError("zeromq python module not found")

        self.ctx = zmq.Context()

        # sanity check config
        if "bind" in self.config:
            if "connect" in self.config:
                msg = "bind and connect are mutually exclusive"
                self.log.critical(msg)
                raise ValueError(msg)

        elif "connect" not in self.config:
            msg = "missing bind or connect"
            self.log.critical(msg)
            raise ValueError(msg)

    def on_start(self):
        self.sock = self.ctx.socket(zmq.PUB)
        if "bind" in self.config:
            self.sock.bind(self.config["bind"])
        elif "connect" in self.config:
            self.sock.connect(self.config["connect"])

    def on_stop(self):
        if self.sock:
            self.sock.close()

    def emit(self, message):
        self.sock.send_json(message)
        self.log.debug("msg" + str(message))
        self.log.debug("[0MQ] sync send")
