"""
vaping io functionality

currently relies on gevent and imports these functions/classes

- `Queue`
- `JoinableQueue`
- `Empty`
- `Thread` (`gevent.Greenlet`)
- `joinall`
- `sleep`
"""

import os
import sys

# namespace imports
if os.name == 'posix' and sys.version_info < (3, 5, 0):
    import subprocess32 as subprocess
else:
    import subprocess

# FIXME
#from gevent import subprocess
from gevent.queue import Queue, JoinableQueue, Empty # noqa
from gevent import Greenlet as Thread # noqa
from gevent import joinall, sleep # noqa
