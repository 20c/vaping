
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from builtins import zip

import vaping
from vaping.io import subprocess

import collections
import datetime
import gevent
from gevent.queue import Queue
import logging
import re
import select
import sys


_KEYDEF = {
    'FLOW': (
        ('type', str),
        ('agent', str),

        # switch ifIndex
        'in_ifidx',
        'out_ifidx',

        'src_mac',
        'dst_mac',
        'ethertype',
        'in_vlan',
        'out_vlan',
        'src_ip',
        'dst_ip',
        'ip_protocol',
        'ip_tos',
        'ip_ttl',
#                'udp_src_port OR tcp_src_port OR icmp_type',
#                'udp_dst_port OR tcp_dst_port OR icmp_code',
        'src_port',
        'dst_port',
        'tcp_flags',
        'packet_size',
        'IP_size',
        'sampling_rate',
    ),
    'CNTR': (
        ('type', str),
        ('agent', str),
        ('ifidx', int),
        ('iftyp', int),
        ('ifspeed', int),
        # 0 = unknown, 1 = full-duplex, 2 = half-duplex, 3 = in, 4 = out
        ('direction', int),
        # bit field with the following bits assigned:
        # bit 0 = ifAdminStatus (0 = down, 1 = up)
        # bit 1 = ifOperStatus (0 = down, 1 = up) */
        ('status', int),
        ('in_oct', int),
        ('in_ucast', int),
        ('in_mcast', int),
        ('in_bcast', int),
        ('in_discard', int),
        ('in_err', int),
        ('in_unk_proto', int),
        ('out_oct', int),
        ('out_ucast', int),
        ('out_mcast', int),
        ('out_bcast', int),
        ('out_discard', int),
        ('out_err', int),
        ('prom_mode', int),
    )
}


def parse_line(line):
    if line.startswith('CNTR'):
        keys = (x[0] for x in _KEYDEF['CNTR'])
        typs = (x[1] for x in _KEYDEF['CNTR'])
        return {k: t(d) for (d, k, t) in zip(line.split(','), keys, typs)}


def calc_rate(last, cur):
    now = datetime.datetime.utcnow()
    time_delta = (now - last['ts']).total_seconds()
    in_delta = cur['in_oct'] - last['data']['in_oct']
    in_bps = in_delta * 8 / time_delta
    print("time_delta=%f in_delta=%d Gbps=%f" % (time_delta, in_delta, old_div(in_bps, 1000000000)))


@vaping.plugin.register('sflowtool')
class SflowTool(vaping.plugins.TimedProbe):

    default_config={
        'interval': '1m',
        'count': 5,
    }

    def init(self):
        self.stdout_queue = Queue()
        self.stderr_queue = Queue()
        args = [
            'sflowtool',
            '-l',
        ]
        self.spawn_process(args)

    def poll_process(self, cmd, stdout, stderr):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            try:
                fds = [proc.stdout.fileno(), proc.stderr.fileno()]
                ret = select.select(fds, [], [])

                for fd in ret[0]:
                    if fd == proc.stdout.fileno():
                        read = proc.stdout.readline()
                        #stdout.append(read)
                    if fd == proc.stderr.fileno():
                        read = proc.stderr.readline()
                        self.log.error("stderr" + read)

                if proc.poll() != None:
                    self.log.warning("poll break")
                    break

                line = proc.stdout.readline()
                #logging.debug(' '.join(cmd))
                if line.startswith('CNTR'):
                    #self.log.debug(line)
                    stdout.put(parse_line(line))

            except Exception as e:
                #self.log.debug(str(e))
                print(e)
                pass

    def spawn_process(self, args):
        #      cmd.extend(self.hosts)
        self.log.debug("spawning " + ' '.join(args))
        gevent.spawn(self.poll_process, args, self.stdout_queue, self.stderr_queue)


    def popen(self, *args):
        """ make cmd command and popen it """
        cmd = ['sflowtool',]
        cmd.extend(args)
#        cmd.extend(self.hosts)
        self.log.debug(' '.join(cmd))

        # get both stdout and stderr
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def msg_init(self):
        self.msg = {}

    def probe(self):
        self.log.debug("stdout queue %d" % self.stdout_queue.qsize())
        if not self.stdout_queue.qsize():
            return {}

        data = []
        try:
        # OPT skip_fields
            while True:
                line = self.stdout_queue.get_nowait()
                data.append(line)

        except gevent.queue.Empty as e:
            pass

        msg = {}
        msg['data'] = data
        msg['ts'] = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
        return msg

