import datetime
import shlex

import munge

import vaping
from vaping.io import subprocess


@vaping.plugin.register("command")
class CommandProbe(vaping.plugins.TimedProbe):

    """
    Probe type plugin that allows you to run an arbitrary
    command for each host and return the command output as
    data

    # Config

    - command (`str`): command to run (use `{host}` to reference the host)
    - interval (`float`): time between probes

    # Instanced Attributes

    - command (`str`): command to run
    """

    default_config = {
        "command": None,
        "interval": "1m",
        "count": 5,
    }

    def init(self):
        if "command" not in self.config:
            raise ValueError("command is required")

        for name, group_config in list(self.groups.items()):
            self.hosts.extend(group_config.get("hosts", []))

        self.command = self.config["command"]

    def probe(self):
        codec = munge.get_codec("yaml")()
        msg = {}
        msg["data"] = []
        msg["ts"] = (
            datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        ).total_seconds()

        # FIXME use poll
        for host in self.hosts:
            args = shlex.split(self.command.format(host=host))
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )

            # TODO poll, timeout, maybe from parent process for better control?
            with proc.stdout:
                # msg['data'].append(proc.stdout.read())
                msg["data"].append(codec.load(proc.stdout))

        return msg
