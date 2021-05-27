import vaping
import vaping.config

try:
    import rrdtool
except ImportError:
    rrdtool = None

import confu.schema

from vaping.plugins import TimeSeriesDBSchema


class RRDToolSchema(TimeSeriesDBSchema):
    """
    Define a schema for FPing and also define defaults.
    """

    step = confu.schema.Int(required=True, help="Passed to rrd tool --step option.")
    data_sources = confu.schema.List(item=confu.schema.Str(), default=[], help="")
    archives = confu.schema.List(item=confu.schema.Str(), default=[])


@vaping.plugin.register("rrd")
class RRDToolPlugin(vaping.plugins.TimeSeriesDB):

    """
    RRDTool plugin that allows vaping to persist data
    in a rrdtool database
    """

    ConfigSchema = RRDToolSchema

    def __init__(self, config, ctx):
        if not rrdtool:
            raise ImportError("rrdtool not found")
        super().__init__(config, ctx)

    def init(self):
        # rrdtool specific config
        self.data_sources = self.config.get("data_sources")
        self.archives = self.config.get("archives")
        self.step = self.config.get("step")

    def create(self, filename):
        rrdtool.create(
            filename, "--step", str(self.step), self.data_sources, *self.archives
        )

    def update(self, filename, time, value):
        if value is None:
            return
        rrdtool.update(filename, "%d:%.4f" % (time, value))
