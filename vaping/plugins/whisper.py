from __future__ import absolute_import

import vaping
import vaping.config

try:
    import whisper
except ImportError:
    whisper = None

@vaping.plugin.register('whisper')
class WhisperPlugin(vaping.plugins.TimeSeriesDB):

    """
    Whisper plugin that allows vaping to persist data
    in a whisper database
    """

    def __init__(self, config, ctx):
        if not whisper:
            raise ImportError("whisper not found")
        super(WhisperPlugin, self).__init__(config, ctx)

        # whisper specific config
        self.retention = self.config.get("retention", ['3s:1d'])
        self.x_files_factor = float(self.config.get("x_files_factor", 0.5))
        self.aggregation_method = self.config.get("aggregation_method", "average")
        self.sparse = bool(self.config.get("sparse", False))

    def start(self):
        # build archives based on retention setting
        # NOTE: if retention is changed in config on an existing database
        # it will have to be rebuilt.
        self.archives = [whisper.parseRetentionDef(x) for x in self.retention]

    def create(self, filename):
        whisper.create(filename, self.archives,
            xFilesFactor=self.x_files_factor,
            aggregationMethod=self.aggregation_method,
            sparse=self.sparse
        )

    def update(self, filename, time, value):
        whisper.update(filename, value, time)

    def get(self, filename, from_time, to_time=None):
        (times, values) = whisper.fetch(filename, from_time, to_time)
        return times, values
