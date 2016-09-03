
import abc
import datetime
import logging

from vaping.config import parse_interval
import vaping.io


class PluginBase(vaping.io.Thread):
    """
    Base plugin class

    Initializes:

    - `self.config` as plugins config
    - `self.log` as a logging object for plugin
    - `self.vaping` as a reference to the main vaping object

    then calls `self.init()`
    """
    def init(self):
        """
        called after the plugin is initialized, plugin may define this for any
        other initialization code
        """
        pass

    def popen(self, args, **kwargs):
        """
        creates a subprocess with passed args
        """
        logging.debug("popen %s", ' '.join(args))
        return vaping.io.subprocess.Popen(args, **kwargs)

    @property
    def log(self):
        if not self._logger:
            self._logger = logging.getLogger('vaping.plugins.' + self.plugin_type)
        return self._logger

    def __init__(self, config, ctx):
        super(PluginBase, self).__init__()

        self.config = config
        self.vaping = ctx
        self._logger = None

        self.init()


class ProbeBase(PluginBase):
    """
    Base class for probe plugin, used for getting data

    expects method probe() to be defined
    """
    __metaclass__ = abc.ABCMeta

    def init(self):
        pass

    @abc.abstractmethod
    def probe(self):
        """
        probe for data, return a list of dicts
        """

    def __init__(self, config, ctx, emit=None):
        self._emit = emit
        super(ProbeBase, self).__init__(config, ctx)

    def _run(self):
        self.run_level = 1
        while self.run_level:
            msg = self.probe()
            if not msg:
                self.log.debug("probe returned no data")
                continue

            # greenlet returns false if not running
            if hasattr(self._emit, 'emit'):
                self.log.debug("sending", msg)
                self._emit.emit(msg)


class TimedProbe(ProbeBase):
    """
    Probe class that calls probe every config defined interval
    """
    def __init__(self, config, ctx, emit=None):
        if 'interval' not in config:
            raise ValueError('interval not set in config')
        self.interval = parse_interval(config['interval'])
        # TODO move to fping
        self.count = int(config.get('count', 0))
        self.run_level = 0

        super(TimedProbe, self).__init__(config, ctx, emit)

    def _run(self):
        self.run_level = 1
        while self.run_level:
            start = datetime.datetime.now()
            msg = self.probe()

            # greenlet returns false if not running
            if hasattr(self._emit, 'emit'):
                if msg:
                    self.log.debug("sending", msg)
                    self._emit.emit(msg)
                else:
                    self.log.debug("probe returned no data")

            done = datetime.datetime.now()
            elapsed = done - start
            if elapsed.total_seconds() > self.interval:
                self.log.warning("probe time exceeded interval")
            else:
                sleeptime = datetime.timedelta(seconds=self.interval) - elapsed
                vaping.io.sleep(sleeptime.total_seconds())


class EmitBase(PluginBase):
    """
    Base class for emit plugins, used for sending data

    expects method probe() to be defined
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, config, ctx):
        super(EmitBase, self).__init__(config, ctx)

    @abc.abstractmethod
    def emit(self, data):
        """ accept data to emit """

