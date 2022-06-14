#

## Plugins

It is not difficult to write plugins for vaping, just inherit from the type you
want to make and put it in the $VAPING_HOME/plugins directory.

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

Then calls alls `self.init()` prefork while loading all modules, init() should
not do anything active, any files opened may be closed when it forks.

Plugins should prefer `init()` to `__init__()` to ensure the class is
completely done initializing.

Calls `self.on_start()` and `self.on_stop()` before and after running in
case any connections need to be created or cleaned up.

#### init

```
init(self)
```

called after the plugin is initialized, plugin may define this for any
other initialization code

#### on_start

```
on_start(self)
```

called when the daemon is starting

#### on_stop

```
on_stop(self)
```

called when the daemon is stopping

#### new_message

```
new_message(self)
```

creates a new message, setting `type`, `source`, `ts`, `data`
- `data` is initialized to an empty array

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

expects method emit() to be defined

#### emit

```
emit(self, message)
```

accept message to emit


