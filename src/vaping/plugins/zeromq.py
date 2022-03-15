try:
    import zmq.asyncio as zmq
    from zmq import PUB
except ImportError:
    zmq = None

import confu.schema

import vaping
import vaping.plugins


class ZeroMQSchema(vaping.plugins.PluginConfigSchema):
    bind = confu.schema.Str(default="")
    connect = confu.schema.Str(default="")


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
        if self.config.get("bind"):
            if self.config.get("connect"):
                msg = "bind and connect are mutually exclusive"
                self.log.critical(msg)
                raise ValueError(msg)
        elif not self.config.get("connect"):
            msg = "missing bind or connect"
            self.log.critical(msg)
            raise ValueError(msg)

    def on_start(self):
        self.sock = self.ctx.socket(PUB)
        if self.config.get("bind"):
            self.sock.bind(self.config["bind"])
        elif self.config.get("connect"):
            self.sock.connect(self.config["connect"])

    def on_stop(self):
        if self.sock:
            self.sock.close()

    def emit(self, message):
        self.sock.send_json(message)
        self.log.debug("msg" + str(message))
        self.log.debug("[0MQ] sync send")
