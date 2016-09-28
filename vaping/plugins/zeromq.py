from builtins import str

try:
    import zmq.green as zmq
except ImportError:
    zmq = None

import vaping
import vaping.plugins


@vaping.plugin.register('zeromq')
class ZeroMQ(vaping.plugins.EmitBase):

    def init(self):
        self.log.debug("init zeromq ..")
        if not zmq:
            self.log.error("missing zeromq, please install pyzmq to use this plugin")
            self.skip = True
            return

        self.skip = False
        self.ctx = zmq.Context()

        # sanity check config
        if 'bind' in self.config:
            if 'connect' in self.config:
                msg = "bind and connect are mutually exclusive"
                self.log.error(msg)
                raise ValueError(msg)

        elif 'connect' not in self.config:
            self.log.warning("skipping zeromq, missing bind or connect")
            self.skip = True

    def on_start(self):
        if self.skip:
            return
        self.sock = self.ctx.socket(zmq.PUB)
        if 'bind' in self.config:
            self.sock.bind(self.config['bind'])
        elif 'connect' in self.config:
            self.sock.connect(self.config['connect'])

    def on_stop(self):
        if self.skip:
            return
        if self.sock:
            self.sock.close()

    def emit(self, data):
        if self.skip:
            return

# TODO option topic
#        self.sock.send_multipart([self.topic, data])
        self.sock.send_json(data)
        self.log.debug("msg" + str(data))
        self.log.debug("[0MQ] sync send")

