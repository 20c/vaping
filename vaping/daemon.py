
from __future__ import absolute_import
from builtins import object

import daemon
import pid as pidfile
import os
import signal
import sys

import logging

import vaping
import vaping.config
import vaping.io
from vaping import plugin


class PluginContext(object):
    """
    Context to pass to plugins for getting extra information
    """
    def __init__(self, config):
        # probably should be a deep copy for security from plugins
        self.__config = config.copy()

    @property
    def config(self):
        return self.__config


class Vaping(object):
    """ Vaping daemon class """

    def __init__(self, config=None, config_dir=None):
        """
        must either pass config as a dict or vaping.config.Config
        or config_dir as a path to where the config dir is located
        """
        if config:
            if isinstance(config, dict):
                self.config = vaping.Config(data=config)
            else:
                if not config.meta:
                    raise ValueError("config was not specified or empty")
                self.config = config
        elif config_dir:
            self.config = vaping.Config(read=config_dir)
        else:
            raise ValueError("config was not specified or empty")

        self.joins = []
        self._logger = None
        self.plugin_context = PluginContext(self.config)

        vcfg = self.config.get('vaping', None)
        if not vcfg:
            vcfg = dict()

        # get either home_dir from config, or use config_dir
        self.home_dir = vcfg.get('home_dir', None)
        if not self.home_dir:
            self.home_dir = self.config.meta['config_dir']

        if not os.path.exists(self.home_dir):
            raise ValueError("home directory '{}' does not exist".format(self.home_dir))

        if not os.access(self.home_dir, os.W_OK):
            raise ValueError("home directory '{}' is not writable".format(self.home_dir))

        # change to home for working dir
        os.chdir(self.home_dir)

        # instantiate all defined plugins
        # TODO remove and let them lazy init?
        plugins = self.config.get('plugins', None)
        if not plugins:
            raise ValueError('no plugins specified')

        plugin.instantiate(self.config['plugins'], self.plugin_context)

        # check that probes don't name clash with plugins
        for probe in self.config.get('probes', []):
            if plugin.exists(probe["name"]):
                raise ValueError("probes may not share names with plugins ({})".format(probe["name"]))

        # TODO move to daemon
        pidname = vcfg.get('pidfile', 'vaping.pid')
        self.pidfile = pidfile.PidFile(pidname=pidname, piddir=self.home_dir)

    @property
    def log(self):
        if not self._logger:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def _exec(self, detach=True):
        """
        daemonize and exec main()
        """
        kwargs = {
            'pidfile': self.pidfile,
            'working_directory': self.home_dir,
            }

        # FIXME - doesn't work
        if not detach:
            kwargs.update({
                'detach_process': False,
                'files_preserve': [0,1,2],
                'stdout': sys.stdout,
                'stderr': sys.stderr,
                })

        ctx = daemon.DaemonContext(**kwargs)

        with ctx:
            self._main()

    def _main(self):
        """
        process
        """
        probes = self.config.get('probes', None)
        if not probes:
            raise ValueError('no probes specified')

        for probe_config in self.config['probes']:
            probe = plugin.get_probe(probe_config, self.plugin_context)
            # FIXME - needs to check for output defined in plugin
            if 'output' not in probe_config:
                raise ValueError("no output specified")

            # get all output targets and start / join them
            for output_name in probe_config['output']:
                output = plugin.get_output(output_name, self.plugin_context)
                if not output.started:
                    output.start()
                    self.joins.append(output)
                probe._emit.append(output)

            probe.start()
            self.joins.append(probe)

        vaping.io.joinall(self.joins)
        return 0

    def start(self):
        """ start daemon """
        self._exec()

    def stop(self):
        """ stop daemon """
        try:
            with self.pidfile:
                self.log.error("failed to stop, missing pid file or not running")

        except pidfile.PidFileError:
            # this isn't exposed in pidfile :o
            with open(self.pidfile.filename) as fobj:
                pid = int(fobj.readline().rstrip())
            if not pid:
                self.log.error("failed to read pid from file")

            self.log.info("killing %d", pid)
            os.kill(pid, signal.SIGTERM)

    def run(self):
        """ run daemon """
        # FIXME - not detaching doesn't work, just run directly for now
        # self._exec(detach=False)
        try:
            with self.pidfile:
                return self._main()

        except pidfile.PidFileError:
            # this isn't exposed in pidfile :o
            self.log.error("failed to get pid lock, already running?")
            return 1

        finally:
            # call on_stop to let them clean up
            for mod in self.joins:
                self.log.debug("stopping %s", mod.name)
                mod.on_stop()

