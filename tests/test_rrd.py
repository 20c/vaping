import pytest
import vaping.plugins.rrd


def test_init():
    data_timeseries_empty = dict(
        filename="file",
        field="field",
        )

    with pytest.raises(TypeError):
        vaping.plugin.get_plugin_class('rrd')(data_timeseries_empty, None)
