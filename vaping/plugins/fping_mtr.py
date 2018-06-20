from __future__ import absolute_import
from __future__ import division

import collections
import datetime
import logging
from scapy.all import (IP, TCP, UDP, sr1)

import vaping
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
        self.mtr_host = self.pluginmgr_config.get("host")

    def get_hosts(self):
        first_ttl = 1
        max_ttl = 24
        timeout = .3
        protocol = "udp"
        port = 33434

        if protocol == "udp":
            proto = UDP(dport=port)
        elif protocol == "tcp":
            proto = TCP(dport=port)
        else:
            raise ValueError("invalid protocol")

        hosts = []
        for i in range(first_ttl, max_ttl):
            pkt = IP(dst=self.mtr_host, ttl=i) / proto

            # send recv 1 packet
            reply = sr1(pkt, verbose=0, timeout=timeout)
            if reply is None:
                # no reply
                # TODO should display this
                continue

            hosts.append(reply.src)
            # icmp dest unreachable
            if reply.type == 3:
                break

        return hosts

    def probe(self):

        self.hosts = self.get_hosts()

        return self._run_proc()
