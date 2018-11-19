from __future__ import absolute_import, division, print_function

import collections
import logging

import vaping
from vaping.io import subprocess
from vaping.util import which


class FPingBase(vaping.plugins.TimedProbe):
    """
    FPing base plugin

    config:
        `command` command to run
        `interval` time between pings
        `count` number of pings to send
        `period` time in milliseconds that fping waits between successive packets to an individual target
    """

    default_config = {
        'command': 'fping',
        'interval': '1m',
        'count': 5,
        'period': 20
    }

    def __init__(self, config, ctx):
        super(FPingBase, self).__init__(config, ctx)

        if not which(self.config['command']):
            self.log.critical("missing fping, install it or set `command` in the fping config")
            raise RuntimeError("fping command not found - install the fping package")

        self.count = int(self.config.get('count', 0))
        self.period = int(self.config.get('period', 0))

    def hosts_args(self):
        """
        hosts list can contain strings specifying a host directly
        or dicts containing a "host" key to specify the host

        this way we can allow passing further config details (color, name etc.)
        with each host as well as simply dropping in addresses for quick
        setup depending on the user's needs
        """

        host_args = []
        for row in self.hosts:
            if isinstance(row, dict):
                host_args.append(row["host"])
            else:
                host_args.append(row)

        # using a set changes the order
        dedupe = list()
        for each in host_args:
            if each not in dedupe:
                dedupe.append(each)
        return dedupe

    def parse_verbose(self, line):
        """
        parse output from verbose format
        """
        try:
            logging.debug(line)
            (host, pings) = line.split(' : ')
            cnt = 0
            lost = 0
            times = []
            pings = pings.strip().split(' ')
            cnt = len(pings)
            for latency in pings:
                if latency == '-':
                    continue
                times.append(float(latency))

            lost = cnt - len(times)
            if lost:
                loss = lost / float(cnt)
            else:
                loss = 0.0

            rv = {
                'host': host.strip(),
                'cnt': cnt,
                'loss': loss,
                'data': times,
                }
            if times:
                rv['min'] = min(times)
                rv['max'] = max(times)
                rv['avg'] = sum(times) / len(times)
                rv['last'] = times[-1]
            return rv

        except Exception as e:
            logging.error("failed to get data: {}".format(e))

    def _run_proc(self):
        args = [
            self.config['command'],
            '-u',
            '-C%d' % self.count,
            '-p%d' % self.period,
            '-e'
        ]
        args.extend(self.hosts_args())
        data = list()

        # get both stdout and stderr
        proc = self.popen(args, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)

        # TODO poll, timeout, maybe from parent process for better control?
        with proc.stdout:
            for line in iter(proc.stdout.readline, b''):
                data.append(self.parse_verbose(line.decode("utf-8")))

        return data


@vaping.plugin.register('fping')
class FPing(FPingBase):
    """
    Run fping on configured hosts

    config:
        `command` command to run
        `interval` time between pings
        `count` number of pings to send
    """

    def init(self):
        self.hosts = []
        for key, value in list(self.config.items()):
            # dict means it's a group
            if isinstance(value, collections.Mapping):
                self.hosts.extend(value['hosts'])

    def probe(self):
        msg = self.new_message()
        msg["data"] = self._run_proc()
        return msg
