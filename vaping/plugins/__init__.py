import abc
import copy
import datetime
import logging
import munge
import os

from future.utils import with_metaclass
from vaping.config import parse_interval
import vaping.io


class PluginBase(vaping.io.Thread):
    """
    Base plugin class

    Initializes:

    - `self.config` as plugins config
    - `self.log` as a logging object for plugin
    - `self.vaping` as a reference to the main vaping object

    Then calls alls `self.init()` prefork while loading all modules, init() should
    not do anything active, any files opened may be closed when it forks.

    Plugins should prefer `init()` to `__init__()` to ensure the class is
    completely done initializing.

    Calls `self.on_start()` and `self.on_stop()` before and after running in
    case any connections need to be created or cleaned up.
    """
    def init(self):
        """
        called after the plugin is initialized, plugin may define this for any
        other initialization code
        """
        pass

    def on_start(self):
        """
        called when the daemon is starting
        """
        pass

    def on_stop(self):
        """
        called when the daemon is stopping
        """
        pass

    def new_message(self):
        """
        creates a new message, setting `type`, `source`, `ts`, `data`
        - `data` is initialized to an empty array
        """
        msg = {}
        msg['data'] = []
        msg['type'] = self.plugin_type
        msg['source'] = self.name
        msg['ts'] = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        return msg

    def popen(self, args, **kwargs):
        """
        creates a subprocess with passed args
        """
        self.log.debug("popen %s", ' '.join(args))
        return vaping.io.subprocess.Popen(args, **kwargs)

    @property
    def log(self):
        if not self._logger:
            self._logger = logging.getLogger('vaping.plugins.' + self.plugin_type)
        return self._logger

    def __init__(self, config, ctx):
        if hasattr(self, 'default_config'):
            self.config = munge.util.recursive_update(copy.deepcopy(self.default_config), copy.deepcopy(config))
        else:
            self.config = config
        # set for pluginmgr
        self.pluginmgr_config = self.config
        self.vaping = ctx
        self.name = self.config.get("name")
        self._logger = None

        super(PluginBase, self).__init__()
        self.init()

    def _run(self):
        self.on_start()


class ProbeBase(with_metaclass(abc.ABCMeta, PluginBase)):
    """
    Base class for probe plugin, used for getting data

    expects method probe() to be defined
    """

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
        super(ProbeBase, self)._run()
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
        super(TimedProbe, self).__init__(config, ctx, emit)

        if 'interval' not in self.pluginmgr_config:
            raise ValueError('interval not set in config')
        self.interval = parse_interval(self.pluginmgr_config['interval'])
        self.run_level = 0


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


class EmitBase(with_metaclass(abc.ABCMeta, PluginBase)):
    """
    Base class for emit plugins, used for sending data

    expects method emit() to be defined
    """

    def __init__(self, config, ctx):
        super(EmitBase, self).__init__(config, ctx)

    @abc.abstractmethod
    def emit(self, message):
        """ accept message to emit """


class TimeSeriesDB(EmitBase):
    """
    Base class for timeseries db storage plugins
    """

    def __init__(self, config, ctx):
        super(TimeSeriesDB, self).__init__(config, ctx)

        # filename template
        self.filename = self.config.get("filename")

        # field name to read the value from
        self.field = self.config.get("field")

        if not self.filename:
            raise ValueError("No filename specified")

        if not self.field:
            raise ValueError("No field specified, field should specify which value to store in the database")


    def create(self, filename):
        """
        Create database

        - `filename`: database filename
        """
        raise NotImplementedError()

    def update(self, filename, time, value):
        """
        Update database

        - `filename`: database filename
        - `time`: timestamp
        - `value`
        """
        raise NotImplementedError()

    def get(self, filename, from_time, to_time):
        """
        Retrieve data from database for the specified
        timespan

        - `filename`: database filename
        - `from_time`: from time
        - `to_time`: to time
        """
        raise NotImplementedError()

    def filename_formatters(self, data, row):
        """
        Returns a dict containing the various filename formatter values

        Values are gotten from the vaping data message as well as the
        currently processed row in the message

        - `data`: vaping message
        - `row`: vaping message data row
        """

        r = {
            "source" : data.get("source"),
            "field" : self.field,
            "type" : data.get("type")
        }
        r.update(**row)
        return r

    def format_filename(self, data, row):
        """
        Returns a formatted filename using the template stored
        in self.filename

        - `data`: vaping message
        - `row`: vaping message data row
        """
        return self.filename.format(**self.filename_formatters(data, row))

    def emit(self, message):
        """
        emit to database
        """
        # handle vaping data that arrives in a list
        if isinstance(message.get("data"), list):
            for row in message.get("data"):


                # format filename from data
                filename = self.format_filename(message, row)

                # create database file if it does not exist yet
                if not os.path.exists(filename):
                    self.create(filename)

                # update database
                self.log.debug("storing time:%d, %s:%.5f in %s" % (
                    message.get("ts"), self.field, row.get(self.field), filename))
                self.update(filename, message.get("ts"), row.get(self.field))
