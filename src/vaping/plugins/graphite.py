import requests

import vaping
import vaping.config

try:
    import graphyte
except ImportError:
    graphyte = None

import confu.schema

from vaping.plugins import TimeSeriesDBSchema


def munge_filename(filename):
    filename = filename.replace(".", "_")
    filename = filename.replace("-", ".")
    return filename


class GraphiteSchema(TimeSeriesDBSchema):
    proto = confu.schema.Str(default="http")
    graphite_host = confu.schema.Str(
        default="127.0.0.1", help="IP address for graphite host."
    )
    prefix = confu.schema.Str(default="vaping")


@vaping.plugin.register("graphite")
class GraphitePlugin(vaping.plugins.TimeSeriesDB):

    """
    Graphite plugin that allows vaping to persist data
    to a graphite via line protocole
    """

    def __init__(self, config, ctx):
        super().__init__(config, ctx)

        if not graphyte:
            self.log.critical(
                "missing graphyte, install it with `pip install graphyte`"
            )
            raise RuntimeError("graphyte not found")

        # get configs

        # FIXME: Add help
        self.proto = self.config.get("proto")
        self.graphite_host = self.config.get("graphite_host")
        self.prefix = self.config.get("prefix")

    def start(self):
        graphyte.init(str(self.graphite_host), prefix=str(self.prefix))

    def create(self, filename):
        return

    def update(self, filename, time, value):

        if value is None:
            return

        filename = munge_filename(filename)
        graphyte.send(f"{filename}", value, time)

    def get(self, filename, from_time, to_time=None):
        filename = munge_filename(filename)

        resp = requests.get(
            "{}://{}/render/?target={}.{}&from={}&format=raw".format(
                self.proto, self.graphite_host, self.prefix, filename, from_time
            )
        )

        if resp.ok:
            data = str(resp.text).rstrip().split("|")

            # create timing tuple
            (metric, fromstamp, tostamp, stepsize) = data[0].split(",")
            times = fromstamp, tostamp, stepsize

            # create values list
            values = []
            for v in data[1].split(","):
                values.append(float(v))

            return times, values
        else:
            raise ValueError("error couldn't get graphite data")
