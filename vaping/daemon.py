
from __future__ import absolute_import

import daemon
import pid as pidfile
import os
import signal
import sys

import gevent
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
    def __init__(self, config=None, config_dir=None):
        if config:
            self.config = config
        elif config_dir:
            self.config = vaping.Config(read=config_dir)
        else:
            raise ValueError("no config specificied")

        self.joins = []
        self._logger = None
        self.plugin_context = PluginContext(self.config)

        vcfg = self.config.get('vaping', {})

        # change to home for working dir
        self.home_dir = os.path.abspath(self.config.meta['config_dir'])
        os.chdir(self.home_dir)

        # instantiate all defined plugins
        # TODO remove and let them lazy init?
        plugin.instantiate(config['plugins'], self.plugin_context)

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
        for probe_config in self.config['probes']:
            probe = plugin.get_probe(probe_config, self.plugin_context)
            # FIXME - needs to check for output defined in plugin
            if 'output' not in probe_config:
                raise ValueError("no output specified")
            if len(probe_config['output']) != 1:
                raise NotImplementedError("only single output is currently supported")
            # get_probe instantiates, need to set _emit
            probe._emit = plugin.get_output(probe_config['output'][0], self.plugin_context)
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

