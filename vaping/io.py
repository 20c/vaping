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
