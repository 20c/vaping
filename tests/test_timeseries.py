import time

import vaping.plugins
from vaping import plugin

config = {
    "type" : "test_tsdb",
    "filename" : "{a}-{b}-{field}",
    "field" : "test"
}

@plugin.register("test_tsdb")
class TSDBTestPlugin(vaping.plugins.TimeSeriesDB):

    """
    Test plugin from the TimeSeriesDB abstraction
    """

    def __init__(self, config, ctx):
        super(TSDBTestPlugin, self).__init__(config, ctx)
        self.updated = {}

    def create(self, filename):
        self.created = True

    def update(self, filename, time, value):
        self.updated[filename] = (time, value)

def test_filename_format():
    """
    test filename formatting from data
    """
    inst = plugin.get_instance(config, None)
    assert inst.format_filename({}, {"a":"first", "b":"second"}) == "first-second-test"

def test_update_and_create():
    """
    test that update() and create() are called accordingly during
    emit()
    """
    inst = plugin.get_instance(config, None)
    t = time.time()
    inst.emit({
        "type" : "test",
        "source" : "test_update_and_create",
        "ts" : t,
        "data" : [
            { "test" : 123, "a" : "row", "b" : "1" },
            { "test" : 456, "a" : "row", "b" : "2" }
        ]
    })
    assert inst.created == True
    assert inst.updated["row-1-test"] == (t, 123)
    assert inst.updated["row-2-test"] == (t, 456)

