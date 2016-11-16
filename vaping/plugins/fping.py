
from __future__ import absolute_import
from __future__ import division
from past.utils import old_div
from builtins import object

import vaping
from vaping.io import subprocess
from vaping.util import which

import collections
import datetime
import logging
import re


class HostGroup(object):
    pass


@vaping.plugin.register('fping')
class FPing(vaping.plugins.TimedProbe):
    """
    config:
        `command` command to run
        `interval` time between pings
        `count` number of pings to send
    """
    re_sum = re.compile('^(?P<host>[\w\.]+)\s+: xmt/rcv/%\w+ = (?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)%, min/avg/max = (?P<min>[\d\.]+)/(?P<avg>[\d\.]+)/(?P<max>[\d\.]+).*')

    default_config={
        'command': 'fping',
        'interval': '1m',
        'count': 5,
    }

    def init(self):
        if not which(self.config['command']):
            self.log.critical("missing fping, install it or set `command` in the fping config")

            raise RuntimeError("fping command not found")

        self.hosts = []
        for k,v in list(self.config.items()):
            # dict means it's a group
            if isinstance(v, collections.Mapping):
                self.hosts.extend(v['hosts'])

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
            if type(row) == dict:
                host_args.append(row["host"])
            else:
                host_args.append(row)
        return list(set(host_args))


    def parse_verbose(self, line):
        try:
            logging.debug(line)
            (host, pings) = line.split(':')
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
                loss = old_div(lost, float(cnt))
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
                rv['avg'] = old_div(sum(times), len(times))
            return rv

        except Exception as e:
            logging.error("failed to get data %s", e)

    def probe(self):
        args = [
            self.config['command'],
            '-u',
            '-C%d' % self.count,
            '-p20',
            '-e'
        ]
        args.extend(self.hosts_args())

        # get both stdout and stderr
        proc = self.popen(args, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)

        msg = {}
        msg['data'] = []
        msg['type'] = "fping"
        msg['source'] = self.name
        msg['ts'] = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()

        # TODO poll, timeout, maybe from parent process for better control?
        with proc.stdout:
            for line in iter(proc.stdout.readline, ''):
                msg['data'].append(self.parse_verbose(line))

        return msg

    def run_sum(self, emitter=None):
        """ run for summary mode """
        re_ts = re.compile('^\[(?P<ts>[\d\:]+)]$')
        re_sum = re.compile('^(?P<host>[\w\.]+)\s+: xmt/rcv/%\w+ = (?P<sent>\d+)/(?P<recv>\d+)/(?P<loss>\d+)%, min/avg/max = (?P<min>[\d\.]+)/(?P<avg>[\d\.]+)/(?P<max>[\d\.]+).*')
        args = [
            'fping',
            '-aA',
            '-l',
            '-p200',
            '-Q1',
        ]

        args.extend(self.hosts_args())

        # get both stdout and stderr
        proc = self.popen(args, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)

        # each summary block is preceeded by a timestamp
        host_count = len(self.hosts) - 1

        # TODO poll, timeout, maybe from parent process for better control?
        with proc.stdout:
            while True:
                msg = {}
                i = 0
                msg['data'] = []
                msg['source'] = self.name
                msg['type'] = "fping"

                # read until getting timestamp message
                for line in iter(proc.stdout.readline, ''):
                    match = re_ts.search(line)
                    if match:
                        msg['ts'] = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()

                        break
                    else:
                        logging.warning("skipping unparsable line '%s'", line)

                for line in iter(proc.stdout.readline, ''):
                    logging.debug(line)
                    match = re_sum.search(line)
                    if match:
                        msg['data'].append(match.groupdict())
                        i += 1
                    else:
                        logging.warning("skipping unparsable line '%s'", line)
                    if i >= len(self.hosts):
                        break

                if emitter:
                    emitter.emit(msg)

