import logging

import vaping
import vaping.plugins.fping
from vaping.io import subprocess


@vaping.plugin.register("fping_mtr")
class FPingMTR(vaping.plugins.fping.FPingBase):
    """
    Run fping on a traceroute path

    # Config

    - interval (`float`) time between pings
    - count (`int`) number of pings to send

    # Instanced Attributes

    - hosts (`list`)
    - lines_read (`int`)
    - mtr_host (`str`)
    """

    def init(self):
        self.hosts = []
        self.lines_read = 0
        self.mtr_host = self.config.get("host")

    def parse_traceroute_line(self, line):
        """
        parse host from verbose traceroute result format

        **Arguments**

        - line (string type): line from traceroutei result output

        **Returns**

        host (`str`)
        """
        try:
            host = line.split()[1].decode("utf8")
            # TODO: do something else if host == "*"?
            if host.strip("*\n"):
                return host

        except Exception as e:
            logging.error(f"failed to get data {e}")

    def parse_traceroute(self, it):
        """
        parse traceroute output

        **Arguments**

        - it: collection of lines to iterate through

        **Returns**

        hosts (`list<str>`): list of hosts in the traceroute result
        """

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
        """
        Run traceroute for the `mtr_host` host and return
        the hosts found in the route

        **Returns**

        hosts (`list<str>`): list of hosts in the route to `mtr_host`
        """

        command = "traceroute"
        # first_ttl = 1
        # max_ttl = 24
        # timeout = 0.3
        # protocol = "udp"
        # port = 33434

        # -f first_ttl
        # -m max_ttl
        args = [
            command,
            "-n",
            # -w wait time seconds
            "-w1",
            # -q number of queries
            "-q1",
            self.mtr_host,
        ]

        # get both stdout and stderr
        proc = self.popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        with proc.stdout:
            hosts = self.parse_traceroute(iter(proc.stdout.readline, b""))
        return hosts

    def probe(self):
        """
        Gets a list of hosts via `get_hosts` and then runs fping
        against all of them to build mtr data

        **Returns**

        msg (`dict`)
        """
        self.hosts = self.get_hosts()
        msg = self.new_message()
        data = {
            hop["host"]: hop
            for hop in self._run_proc()
            if hop and hop["host"] in self.hosts
        }

        msg["data"] = [
            dict(
                hops=self.hosts,
                host=self.mtr_host,
                data=data,
            ),
        ]
        return msg
