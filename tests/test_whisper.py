import pytest
import time
import sys

#FIXME: take this condition out once whisper supports py3
if sys.version_info <= (2,9):
    import vaping.plugins.whisper

from vaping import plugin

config = {
    "type" : "whisper",
    "name" : "whisper_test",
    "retention" : ["1s:1d"],
    "field" : "test"
}

FILENAME_TEMPLATE = "{id}-{field}.wsp"

#FIXME: make sure to test py3 once whipser supports it
@pytest.mark.skipif(sys.version_info > (2,9), reason="whisper does not support py3 at this point")
def test_whisper(tmpdir):
    """
    test whisper-db creation and update from emit
    """

    config["filename"] = str(tmpdir.mkdir("whisper").join(FILENAME_TEMPLATE))
    inst = plugin.get_instance(config, None)
    inst.start()
    i = 0
    t = int(time.time())-10

    # emit and insert 10 data points for 2 graphs at 1 second intervals
    while i < 10:
        inst.emit({
            "type" : "test",
            "source" : "test_whisper",
            "ts" : t+i,
            "data" : [
                { "test" : 123+i, "id" : 1 },
                { "test" : 456+i, "id" : 2 }
            ]
        })
        i += 1

    # retrieve data from whisper db
    times_1, values_1 = inst.get(inst.format_filename({}, {"id":1}), t - 1, t + 9)
    times_2, values_2 = inst.get(inst.format_filename({}, {"id":2}), t - 1, t + 9)

    assert times_1[0] == t
    assert times_1[1] == t+10
    assert times_1[2] == 1

    assert times_2[0] == t
    assert times_2[1] == t+10
    assert times_2[2] == 1

    def value_assert(points, start):
        i = 0
        for k in points:
            assert k == start + i
            i += 1

    value_assert(values_1, 123)
    value_assert(values_2, 456)
