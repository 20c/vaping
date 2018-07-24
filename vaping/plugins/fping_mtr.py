from __future__ import absolute_import
from __future__ import division

import logging

import vaping
import vaping.plugins.fping
from vaping.io import subprocess
from vaping.util import which


@vaping.plugin.register('fping_mtr')
class FPingMTR(vaping.plugins.fping.FPingBase):
    """
    Run fping on a traceroute path

    config:
        `command` command to run
        `interval` time between pings
        `count` number of pings to send
    """

    def init(self):
        self.hosts = []
        self.lines_read = 0
        self.mtr_host = self.config.get("host")

    def parse_traceroute_line(self, line):
        """
        parse output from verbose format
        """
        try:
            logging.debug(line)
            host = line.split()[1]
            if host != "*":
                return str(host)

        except Exception as e:
            logging.error("failed to get data {}".format(e))

    def parse_traceroute(self, it):
        self.lines_read = 0
        hosts = list()

        for line in it:
            self.lines_read += 1
            # skip first line
            if self.lines_read == 1:
                continue
            host = self.parse_traceroute_line(line)
            if host and host not in hosts:
                hosts.append(host)

        if not len(hosts):
            raise Exception("no path found")
        return hosts

    def get_hosts(self):
        command = "traceroute"
        first_ttl = 1
        max_ttl = 24
        timeout = .3
        protocol = "udp"
        port = 33434

        # -f first_ttl
        # -m max_ttl
        args = [
            command,
            '-n',
            # -w wait time seconds
            '-w1',
            # -q number of queries
            '-q1',
            self.mtr_host,
        ]

        # get both stdout and stderr
        proc = self.popen(args, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)

        with proc.stdout:
            hosts = self.parse_traceroute(iter(proc.stdout.readline, b''))
        return hosts

    def probe(self):
        self.hosts = self.get_hosts()
        msg = self.new_message()
        data = dict([(hop["host"],hop) for hop in self._run_proc()
                     if hop and hop["host"] in self.hosts])

        msg["data"] = [
            dict(
                hops=self.hosts,
                host=self.mtr_host,
                data=data,
                ),
            ]
        return msg
