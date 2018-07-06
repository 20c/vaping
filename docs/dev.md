
#

## Plugins

It's quite easy to write plugins for vaping, just inherit from the type you
want o make and put it in your $VAPING_HOME/plugins directory.

To make a probe that executes at a user configurable time like fping, simply
import vaping, @register it's name, inherit from `vaping.plugins.TimedProbe`,
and define `probe()`. Vaping will take care of the rest, including threading
and IO multiplexing.

For example, create the following at `$VAPING_HOME/plugins/plugin_name.py`:

```py
import vaping


@vaping.plugin.register('plugin_name')
class FPing(vaping.plugins.TimedProbe):
    # called when the class is instantiated
    def init(self):
        pass

    # called when it needs data
    def probe(self):
        return []

```

Then to use it, in your config file, add:

```yaml
probes:
  - name: new probe
    type: plugin_name
    interval: 3s
    output:
      - web
```

And Vaping will call `probe()` every 3 seconds.


## Classes

### PluginBase

```
PluginBase(vaping.io.Thread)
```

Base plugin class

Initializes:

- `self.config` as plugins config
- `self.log` as a logging object for plugin
- `self.vaping` as a reference to the main vaping object

then calls `self.init()`

#### init

```
init(self)
```

called after the plugin is initialized, plugin may define this for any
other initialization code

#### popen

```
popen(self, args, **kwargs)
```

creates a subprocess with passed args


### ProbeBase

```
ProbeBase(vaping.plugins.PluginBase)
```

Base class for probe plugin, used for getting data

expects method probe() to be defined

#### probe

```
probe(self)
```

probe for data, return a list of dicts


### TimedProbe

```
TimedProbe(vaping.plugins.ProbeBase)
```

Probe class that calls probe every config defined interval


### EmitBase

```
EmitBase(vaping.plugins.PluginBase)
```

Base class for emit plugins, used for sending data

expects method probe() to be defined

#### emit

```
emit(self, data)
```

accept data to emit 


