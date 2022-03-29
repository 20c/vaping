import abc
import collections.abc
import copy
import datetime
import logging
import os

import confu.schema
import munge

import vaping.io
from vaping.config import parse_interval


class PluginConfigSchema(confu.schema.Schema):
    """
    Configuration Schema for [PluginBase](#pluginbase)

    When creating new configuration schemas for extended plugins
    extend this.
    """

    name = confu.schema.Str("name", help="Plugin name")
    type = confu.schema.Str("type", help="Plugin type")


class PluginBase(vaping.io.Thread):
    """
    Base plugin interface

    # Class Attributes

    - lazy_start (`bool`=`False`): if `True` plugin will not be
      started on vaping start, but when at a later point (usually
      when it starts emitting). Note that the plugin itself will
      need to call `self.start()` somewhere explicitly when this is `True`.

    # Instanced Attributes

    - config (`dict`): plugin config
    - vaping: reference to the main vaping object

    Calls `self.init()` prefork while loading all modules, init() should
    not do anything active, any files opened may be closed when it forks.

    Plugins should prefer `init()` to `__init__()` to ensure the class is
    completely done initializing.

    Calls `self.on_start()` and `self.on_stop()` before and after running in
    case any connections need to be created or cleaned up.
    """

    lazy_start = False

    ConfigSchema = PluginConfigSchema
    ConfigSchema.help = "Base plugin config schema"

    @property
    def groups(self):

        """
        `dict` - group configurations keyed by name
        """

        group_config = {}

        # legacy way of threating any dict as a potential
        # group config (pre #44 implementation)
        # supported until vaping 2.0

        for k, v in list(self.config.items()):
            if isinstance(v, collections.abc.Mapping):
                group_config[k] = v

        # explicit groups object (#44 implementation)

        for _group_config in self.config.get("groups", []):
            group_config[_group_config["name"]] = _group_config

        return group_config

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
        creates and returns new message `dict`, setting `type`, `source`, `ts`, `data`

        `data` is initialized to an empty array

        **Returns**

        message (`dict`)
        """
        msg = {}
        msg["data"] = []
        msg["type"] = self.plugin_type
        msg["source"] = self.name
        msg["ts"] = (
            datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        ).total_seconds()
        return msg

    def popen(self, args, **kwargs):
        """
        creates a subprocess with passed args

        **Returns**

        Popen instance
        """
        self.log.debug("popen %s", " ".join(args))
        return vaping.io.subprocess.Popen(args, **kwargs)

    @property
    def log(self):
        """
        logger instance for plugin type
        """
        if not self._logger:
            self._logger = logging.getLogger("vaping.plugins." + self.plugin_type)
        return self._logger

    def __init__(self, config, ctx):
        """
        **Arguments**

        - config (`dict`)
        - ctx: vaping context
        """

        # FIXME: figure out what from this we want to keep
        if hasattr(self, "default_config"):
            self.config = munge.util.recursive_update(
                copy.deepcopy(self.default_config), copy.deepcopy(config)
            )
        else:
            self.config = config

        if hasattr(self, "ConfigSchema"):
            confu.schema.apply_defaults(self.ConfigSchema(), config)

        # set for pluginmgr
        self.pluginmgr_config = self.config
        self.vaping = ctx
        self.name = self.config.get("name")
        self._logger = None
        self.lazy_start = False
        self.started = False

        super().__init__()
        self.init()

    async def _run(self):
        self.on_start()


class ProbeBase(PluginBase, metaclass=abc.ABCMeta):
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
        if emit:
            self._emit = [emit]
        else:
            self._emit = []

        self._emit_queue = vaping.io.Queue()
        super().__init__(config, ctx)

    async def _run(self):
        super()._run()
        self.on_start()
        self.run_level = 1
        while self.run_level:
            self.send_emission()
            msg = self.probe()
            if msg:
                await self.queue_emission(msg)
            else:
                self.log.debug("probe returned no data")

            await vaping.io.sleep(0.1)

    async def queue_emission(self, msg):
        """
        queue an emission of a message for all output plugins

        **Arguments**

        - msg (`dict`): dict containing `type`, `source`, `ts` and `data` keys
        """
        if not msg:
            return
        for _emitter in self._emit:
            if not hasattr(_emitter, "emit"):
                continue

            async def emit(emitter=_emitter):
                self.log.debug(f"emit to {emitter.name}")
                emitter.emit(msg)

            self.log.debug(
                "queue emission to {} ({})".format(
                    _emitter.name, self._emit_queue.qsize()
                )
            )
            await self._emit_queue.put(emit)

    async def send_emission(self):
        """
        emit and remove the first emission in the queue
        """
        if self._emit_queue.empty():
            return
        emit = self._emit_queue.get_nowait()
        await emit()

    async def emit_all(self):
        """
        emit and remove all emissions in the queue
        """
        while not self._emit_queue.empty():
            await self.send_emission()


class TimedProbeSchema(PluginConfigSchema):
    interval = confu.schema.Str()


class TimedProbe(ProbeBase):
    """
    Probe class that calls probe every config defined interval
    """

    ConfigSchema = TimedProbeSchema

    def __init__(self, config, ctx, emit=None):
        super().__init__(config, ctx, emit)

        if "interval" not in self.pluginmgr_config:
            raise ValueError("interval not set in config")
        self.interval = parse_interval(self.pluginmgr_config["interval"])
        self.run_level = 0

    async def _run(self):
        self.run_level = 1
        while self.run_level:

            start = datetime.datetime.now()

            # since the TimedProbe will sleep between cycles
            # we need to emit all queued emissions each cycle
            await self.emit_all()

            msg = self.probe()

            if msg:
                await self.queue_emission(msg)
            else:
                self.log.debug("probe returned no data")

            done = datetime.datetime.now()
            elapsed = done - start
            if elapsed.total_seconds() > self.interval:
                self.log.warning("probe time exceeded interval")
            else:
                sleeptime = datetime.timedelta(seconds=self.interval) - elapsed
                await vaping.io.sleep(sleeptime.total_seconds())


class FileProbeSchema(PluginConfigSchema):
    path = confu.schema.Str()
    backlog = confu.schema.Int(default=10)
    max_lines = confu.schema.Int(default=1000)


class FileProbe(ProbeBase):
    """
    Probes a file and emits everytime a new line is read

    # Config

    - path (`str`): path to file
    - backlog (`int=0`): number of bytes to read from backlog
    - max_lines (`int=1000`): maximum number of lines to read during probe

    # Instanced Attributes

    - path (`str`): path to file
    - backlog (`int`): number of bytes to read from backlog
    - max_lines (`int`): maximum number of liens to read during probe
    - fh (`filehandler`): file handler for opened file (only available if `path` is set)
    """

    ConfigSchema = FileProbeSchema

    def __init__(self, config, ctx, emit=None):
        super().__init__(config, ctx, emit)
        self.path = self.pluginmgr_config.get("path")
        self.run_level = 0
        self.backlog = int(self.pluginmgr_config.get("backlog", 0))
        self.max_lines = int(self.pluginmgr_config.get("max_lines", 1000))

        if self.path:
            self.fh = open(self.path)
            self.fh.seek(0, 2)

            if self.backlog:
                try:
                    self.fh.seek(self.fh.tell() - self.backlog, os.SEEK_SET)
                except ValueError as exc:
                    if str(exc).find("negative seek position") > -1:
                        self.fh.seek(0)
                    else:
                        raise

    async def _run(self):
        self.run_level = 1
        while self.run_level:
            self.send_emission()
            for msg in self.probe():
                await self.queue_emission(msg)

            await vaping.io.sleep(0.1)

    def validate_file_handler(self):
        """
        Here we validate that our filehandler is pointing
        to an existing file.

        If it doesnt, because file has been deleted, we close
        the filehander and try to reopen
        """
        if self.fh.closed:
            try:
                self.fh = open(self.path)
                self.fh.seek(0, 2)
            except OSError as err:
                logging.error(f"Could not reopen file: {err}")
                return False

        open_stat = os.fstat(self.fh.fileno())
        try:
            file_stat = os.stat(self.path)
        except OSError as err:
            logging.error(f"Could not stat file: {err}")
            return False

        if open_stat != file_stat:
            self.log
            self.fh.close()
            return False

        return True

    def probe(self):
        """
        Probe the file for new lines
        """

        # make sure the filehandler is still valid
        # (e.g. file stat hasnt changed, file exists etc.)
        if not self.validate_file_handler():
            return []

        messages = []

        # read any new lines and push them onto the stack
        for line in self.fh.readlines(self.max_lines):
            data = {"path": self.path}
            msg = self.new_message()

            # process the line - this is where parsing happens
            parsed = self.process_line(line, data)
            if not parsed:
                continue
            data.update(parsed)

            # process the probe - this is where data assignment
            # happens
            data = self.process_probe(data)
            msg["data"] = [data]
            messages.append(msg)

        # process all new messages before returning them
        # for emission
        messages = self.process_messages(messages)

        return messages

    def process_line(self, line, data):
        """override this - parse your line in here"""
        return data

    def process_probe(self, data):
        """override this - assign your data values here"""
        return data

    def process_messages(self, messages):
        """
        override this - process your messages before they
        are emitted
        """

        return messages


class EmitBase(PluginBase, metaclass=abc.ABCMeta):
    """
    Base class for emit plugins, used for sending data

    expects method emit() to be defined
    """

    def __init__(self, config, ctx):
        super().__init__(config, ctx)

    @abc.abstractmethod
    def emit(self, message):
        """accept message to emit"""


class TimeSeriesDBSchema(PluginConfigSchema):
    filename = confu.schema.Str(help="database file name template")
    field = confu.schema.Str(help="field name to read the value from")


class TimeSeriesDB(EmitBase):
    """
    Base interface for timeseries db storage plugins

    # Config

    - filename (`str`): database file name template
    - field (`str`): field name to read the value from

    # Instanced Attributes

    - filename (`str`): database file name template
    - field (`str`): fieeld name to read the value from
    """

    ConfigSchema = TimeSeriesDBSchema

    def __init__(self, config, ctx):
        super().__init__(config, ctx)

        # filename template
        self.filename = self.config.get("filename")

        # field name to read the value from
        self.field = self.config.get("field")

        if not self.filename:
            raise ValueError("No filename specified")

        if not self.field:
            raise ValueError(
                "No field specified, field should specify which value to store in the database"
            )

    def create(self, filename):
        """
        Create database

        **Arguments**

        - filename (`str`): database filename
        """
        raise NotImplementedError()

    def update(self, filename, time, value):
        """
        Update database

        **Arguments**

        - filename (`str`): database filename
        - time (`int`): epoch timestamp
        - value (`mixed`)
        """
        raise NotImplementedError()

    def get(self, filename, from_time, to_time):
        """
        Retrieve data from database for the specified
        timespan

        **Arguments**

        - filename (`str`): database filename
        - from_time (`int`): epoch timestamp start
        - to_time (`int`): epoch timestamp end
        """
        raise NotImplementedError()

    def filename_formatters(self, data, row):
        """
        Returns a dict containing the various filename formatter values

        Values are gotten from the vaping data message as well as the
        currently processed row in the message

        **Arguments**

        - data (`dict`): vaping message
        - row (`dict`): vaping message data row

        **Returns**

        formatter variables (`dict`)
        """

        r = {
            "source": data.get("source"),
            "field": self.field,
            "type": data.get("type"),
        }
        r.update(**row)
        return r

    def format_filename(self, data, row):
        """
        Returns a formatted filename using the template stored
        in self.filename

        **Arguments**

        - data (`dict`): vaping message
        - row (`dict`): vaping message data row

        **Returns**

        formatted version of self.filename (`str`)
        """
        return self.filename.format(**self.filename_formatters(data, row))

    def emit(self, message):
        """
        emit to database

        **Arguments**

        - message (`dict`): vaping message dict
        """
        # handle vaping data that arrives in a list
        if isinstance(message.get("data"), list):
            for row in message.get("data"):

                if row is None:
                    self.log.debug(
                        "Ignoring empty row from {}/{}".format(
                            message.get("source"), message.get("type")
                        )
                    )
                    continue

                # format filename from data
                filename = self.format_filename(message, row)

                # create database file if it does not exist yet
                if not os.path.exists(filename):
                    self.create(filename)

                # update database
                self.log.debug(
                    "storing time:%d, %s:%s in %s"
                    % (
                        message.get("ts"),
                        self.field,
                        row.get(self.field, "-"),
                        filename,
                    )
                )
                self.update(filename, message.get("ts"), row.get(self.field))
