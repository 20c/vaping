from prometheus_client import Counter, Gauge, Summary, start_http_server

import vaping
import vaping.plugins

min_latency = Summary(
    "minimum_latency_milliseconds", "Minimum latency in milliseconds.", ["host"]
)  # NOQA
max_latency = Summary(
    "maximum_latency_milliseconds", "Maximum latency in milliseconds.", ["host"]
)  # NOQA
avg_latency = Summary(
    "average_latency_milliseconds", "Average latency in milliseconds.", ["host"]
)  # NOQA
sent_packets = Counter(
    "number_of_packets_sent", "Number of pings sent to host.", ["host"]
)  # NOQA
packet_loss = Gauge("packet_loss", "% packet loss to host (0-100)", ["host"])  # NOQA


@vaping.plugin.register("prometheus")
class Prometheus(vaping.plugins.EmitBase):
    def init(self):
        self.log.debug("init prometheus plugin")
        port = self.pluginmgr_config.get("port", 9099)
        start_http_server(port)

    def emit(self, data):
        raw_data = data.get("data")

        self.log.debug("data: " + str(raw_data))
        for host_data in raw_data:
            if host_data is None:
                continue

            host_name = host_data.get("host")
            if "min" in host_data:
                min_latency.labels(host_name).observe(host_data.get("min"))
            if "max" in host_data:
                max_latency.labels(host_name).observe(host_data.get("max"))
            if "avg" in host_data:
                avg_latency.labels(host_name).observe(host_data.get("avg"))
            sent_packets.labels(host_name).inc(host_data.get("cnt"))
            packet_loss.labels(host_name).set(host_data.get("loss") * 100)
