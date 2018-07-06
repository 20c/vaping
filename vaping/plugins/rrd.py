from __future__ import absolute_import

import vaping
import vaping.config

try:
    import rrdtool
except ImportError:
    rrdtool = None

@vaping.plugin.register('rrd')
class RRDToolPlugin(vaping.plugins.TimeSeriesDB):

    """
    RRDTool plugin that allows vaping to persist data
    in a rrdtool database
    """

    def __init__(self, config, ctx):
        if not rrdtool:
            raise ImportError("rrdtool not found")
        super(RRDToolPlugin, self).__init__(config, ctx)


    def init(self):
        # rrdtool specific config
        self.data_sources = self.config.get("data_sources", [])
        if not isinstance(self.data_sources, list):
            raise TypeError("data_sources config needs to be of type: list")

        self.archives = self.config.get("archives", [])
        if not isinstance(self.archives, list):
            raise TypeError("archives config needs to be of type: list")

        try:
            self.step = int(self.config.get("step"))
        except TypeError:
            raise TypeError("step config needs to be of type: int")

    def create(self, filename):
        rrdtool.create(
            filename,
            "--step",
            str(self.step),
            self.data_sources,
            *self.archives
        )

    def update(self, filename, time, value):
        rrdtool.update(filename, "%d:%.4f" % (time, value))
