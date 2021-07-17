"""
vaping io functionality
"""


import asyncio
import subprocess  # noqa

import vaping.asyncio_backport as asyncio_backport


async def sleep(seconds):
    await asyncio.sleep(seconds)


if hasattr(asyncio, "run"):
    # py37+
    asyncio_run = asyncio.run
else:
    # py36
    asyncio_run = asyncio_backport.run


def join_plugins(plugins):
    tasks = []

    async def run_plugins():
        for plugin in plugins:
            tasks.append(plugin._run())
        await asyncio.gather(*tasks)

    asyncio_run(run_plugins())


class Queue(asyncio.Queue):
    pass


class Thread:
    def start(self):
        self.started = True
        return
