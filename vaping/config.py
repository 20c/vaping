from __future__ import division

import re

import munge


def parse_interval(val):
    """
    converts a string to float of seconds
        .5 = 500ms
    """
    re_intv = re.compile(r"(?P<count>\d+)(?P<unit>\w+)")
    match = re_intv.match(val.strip())
    if not match:
        raise ValueError("invalid interval string '%s'" % val)
    unit = match.group('unit')
    count = float(match.group('count'))
    if unit == 's':
        return count
    if unit == 'm':
        return count * 60
    if unit == 'ms':
        return count / 1000
    if unit == 'h':
        return count * 3600
    if unit == 'd':
        return count * 86400

    raise ValueError("unknown unit from interval string '%s'" % val)

class Config(munge.Config):
    defaults = {
        'config': {
            'vaping': {
                'home_dir': None,
                'pidfile': 'vaping.pid',
                'plugin_path': [],
                },
            },
        'config_dir': '~/.vaping',
        'codec': 'yaml',
        }
