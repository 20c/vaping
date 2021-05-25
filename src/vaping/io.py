"""
vaping io functionality
"""
import asyncio
import os

import subprocess  # noqa


async def sleep(seconds):
    await asyncio.sleep(seconds)


def join_plugins(plugins):
    tasks = []

    async def run_plugins():
        for plugin in plugins:
            tasks.append(plugin._run())
        await asyncio.gather(*tasks)

    asyncio.run(run_plugins())


class Queue(asyncio.Queue):
    pass


class Thread:
    def start(self):
        self.started = True
        return
