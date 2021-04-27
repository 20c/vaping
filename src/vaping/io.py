"""
vaping io functionality
"""

import os
import sys
import asyncio
import time

# namespace imports
if os.name == "posix" and sys.version_info < (3, 5, 0):
    import subprocess32 as subprocess
else:
    import subprocess


async def sleep(seconds):
    await asyncio.sleep(seconds)

def join_plugins(plugins):
    tasks = []
    async def run_plugins():
        for plugin in plugins:
            tasks.append(plugin._run())
        print("running plugins", tasks, plugins)
        await asyncio.gather(*tasks)
    asyncio.run(run_plugins())

class Queue(asyncio.Queue):
    pass

class Thread(object):

    def start(self):
        self.started = True
        return
