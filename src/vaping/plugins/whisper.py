import vaping
import vaping.config

try:
    import whisper
except ImportError:
    whisper = None

import confu.schema

from vaping.plugins import TimeSeriesDBSchema


class WhisperSchema(TimeSeriesDBSchema):
    """
    Define a schema for FPing and also define defaults.
    """

    retention = confu.schema.List(item=confu.schema.Str(), default=["3s:1d"])
    x_files_factor = confu.schema.Float(default=0.5)
    aggregation_method = confu.schema.Str(default="average")
    sparse = confu.schema.Bool(default=False)


@vaping.plugin.register("whisper")
class WhisperPlugin(vaping.plugins.TimeSeriesDB):

    """
    Whisper plugin that allows vaping to persist data
    in a whisper database
    """

    ConfigSchema = WhisperSchema

    def __init__(self, config, ctx):
        if not whisper:
            raise ImportError("whisper not found")
        super().__init__(config, ctx)

        # whisper specific config
        self.retention = self.config.get("retention")
        self.x_files_factor = self.config.get("x_files_factor")
        self.aggregation_method = self.config.get("aggregation_method")
        self.sparse = self.config.get("sparse")

    def start(self):
        # build archives based on retention setting
        # NOTE: if retention is changed in config on an existing database
        # it will have to be rebuilt.
        self.archives = [whisper.parseRetentionDef(x) for x in self.retention]

    def create(self, filename):
        whisper.create(
            filename,
            self.archives,
            xFilesFactor=self.x_files_factor,
            aggregationMethod=self.aggregation_method,
            sparse=self.sparse,
        )

    def update(self, filename, time, value):
        if value is None:
            return
        whisper.update(filename, value, time)

    def get(self, filename, from_time, to_time=None):
        (times, values) = whisper.fetch(filename, from_time, to_time)
        return times, values
