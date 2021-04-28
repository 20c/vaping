import vaping


def test_init():
    data_timeseries_empty = dict(
        filename="file",
        field="field",
    )

    vaping.plugin.get_plugin_class("graphite")(data_timeseries_empty, None)
