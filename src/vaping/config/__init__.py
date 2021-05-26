import re

import munge

from vaping.config.schema import *  # noqa


def parse_interval(val):
    """
    converts a string to float of seconds
        .5 = 500ms
        90 = 1m30s

    **Arguments**

    - val (`str`)
    """
    re_intv = re.compile(r"([\d\.]+)([a-zA-Z]+)")
    val = val.strip()

    total = 0.0
    for match in re_intv.findall(val):
        unit = match[1]
        count = float(match[0])
        if unit == "s":
            total += count
        elif unit == "m":
            total += count * 60
        elif unit == "ms":
            total += count / 1000
        elif unit == "h":
            total += count * 3600
        elif unit == "d":
            total += count * 86400
        else:
            raise ValueError("unknown unit from interval string '%s'" % val)
    return total


class Config(munge.Config):
    """
    Vaping config manager
    """

    defaults = {
        "config": {
            "vaping": {
                "home_dir": None,
                "pidfile": "vaping.pid",
                "plugin_path": [],
            },
        },
        "config_dir": "~/.vaping",
        "codec": "yaml",
    }
