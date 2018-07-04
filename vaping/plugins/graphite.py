from __future__ import absolute_import

import vaping
import vaping.config
import requests

try:
    import graphyte
except ImportError:
    graphite = None

@vaping.plugin.register('graphite')
class GraphitePlugin(vaping.plugins.TimeSeriesDB):

    """
    Graphite plugin that allows vaping to persist data
    to a graphite via line protocole
    """

    def __init__(self, config, ctx):

        super(GraphitePlugin, self).__init__(config, ctx)

        # get configs
        self.proto = self.pluginmgr_config.get("proto", "http")
        self.graphite_host = self.pluginmgr_config.get("graphite_host", "127.0.0.1")
        self.prefix = self.pluginmgr_config.get("prefix", "vaping")


    def start(self):
        graphyte.init(str(self.graphite_host), prefix=str(self.prefix))

    def create(self, filename):
        return

    def update(self, filename, time, value):
        filename = filename.replace('.','_')
        filename = filename.replace('-','.')
        graphyte.send('{}'.format(filename), value, time)

    def get(self, filename, from_time, to_time=None):
        filename = filename.replace('.','_')
        filename = filename.replace('-','.')

        resp = requests.get("{}}://{}/render/?target={}.{}&from={}&format=raw".format(
            self.proto,self.graphite_host,self.prefix,filename,from_time))

        if resp.ok:
            data = str(resp.text).rstrip().split('|')

            #create timing tuple
            (metric, fromstamp, tostamp, stepsize) = data[0].split(',')
            times = fromstamp, tostamp, stepsize

            #create values list
            values = []
            for v in  data[1].split(','):
                values.append(float(v))

            return times, values
        else:
            raise ValueError("error couldn't get graphite data")

