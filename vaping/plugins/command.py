from __future__ import absolute_import

import collections
import datetime
import munge
import shlex

import vaping
from vaping.io import subprocess


@vaping.plugin.register('command')
class CommandProbe(vaping.plugins.TimedProbe):

    default_config = {
        'command': None,
        'interval': '1m',
        'count': 5,
    }

    def init(self):
        if 'command' not in self.config:
            raise ValueError('command is required')

        for k, v in list(self.config.items()):
            # dict means it's a group - FIXME explicit groups
            if isinstance(v, collections.Mapping):
                self.hosts = v['hosts']

        self.command = self.config['command']

    def probe(self):
        codec = munge.get_codec('yaml')()
        msg = {}
        msg['data'] = []
        msg['ts'] = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()

        # FIXME use poll
        for host in self.hosts:
            args = shlex.split(self.command.format(host=host))
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            # TODO poll, timeout, maybe from parent process for better control?
            with proc.stdout:
                #msg['data'].append(proc.stdout.read())
                msg['data'].append(codec.load(proc.stdout))

        return msg

