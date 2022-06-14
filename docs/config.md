## Introduction

Vaping will look for its config directory in the following order:

- command line option `--home`
- environment variable `$VAPING_HOME`
- `.vaping` in the current working directory
- `$APP_DIR/vaping` (`.config/vaping/` or `.vaping/` on most systems).

By default it uses YAML config files, but will also support JSON, which it determines by file extension, for example `$VAPING_HOME/config.yml`

## Default Config

```yaml
vaping:
  pidfile: vaping.pid
  plugin_path: []

probes:

plugins:
```

## Plugins

The `plugins` section is a list defining which plugins are loaded and possibly configured to share between anything else referencing it. Each must define `type`, which can either be a plugin type, or the name of a previously defined type. To reference it later, `name` must be defined.

### fping

- `command` command to run
- `interval` time between pings
- `count` number of pings to send
- `period` time in milliseconds that fping waits between successive packets to an individual target

For example, the default of

```yml
interval: 1m
count: 5
period: 20
```

sends 5 pings to each host every minute, with 20 milliseconds between each one.

### whisper

Config options for whisper plugin:

- `retention` is a list of `$time_per_data_point:$length_to_store`
- `filename` is the path/name of the file you'd like to write the data to
- `field` is the values you want to retrieve from. i.e. avg, max, min

Variables:

- `source` - the probe the data will be received from
- `host` - the IP/FQDN of the host being monitored
- `field` - the field being written to whisper

For example:

```yml
plugins:
  - name: whisper_avg
    type: whisper

    # will create one file per host
    # for example: latency-8.8.8.8-avg
    filename: '{source}-{host}-{field}.wsp'

    # specified which field to retrieve the value from
    field: avg

    # whisper configuration
    aggregation_method: average
    sparse: false
    x_files_factor: 0.5
    retention:
      - 60:1440 # 60 seconds per datapoint, 1440 datapoints = 1 day of retention
      - 15m:8 # 15 minutes per datapoint, 8 datapoints = 2 hours of retention
      - 1h:7d # 1 hour per datapoint, 7 days of retention
      - 12h:2y # 12 hours per datapoint, 2 years of retention
```

Full example: `examples/whisper/config.yml`

## Probes

The `probes` section is a list defining input sections. It must define at least `type` which may refer directly to a plugin type, or to a config defined type.

Probes may not use the same name as any plugin.

The `probes` section also contains `output`, which is a list of plugins for sending results to another service like zeromq or whisper database.

Example:

```yml
probes:
  - name: latency
    type: std_fping
    output:
      - whisper_avg
      - zmq_vodka
```

## Custom Layouts - Graphsrv

It is possible for you to add / edit your layouts. You can use this to add additional rows/columns to the display grid.

### Basic Layout example:
Create a `layout.yml` file.
```
layouts:
  ## INDEX #####################################################################

  index:
    type: index
    grid: 3x3
    graph:
      config: multitarget
      fit: "yes"
      targets: all

  ## DETAIL ####################################################################

  detail:
    type: custom
    layout:
      # row 1
      - cols:
          # col 1, render a graph
          - graph:
              config: multitarget

              # fit to column
              fit: "yes"

              # render all targets to this graph
              targets: all

              # custom graph id
              id: multitarget-1
            width: 12
        height: 100
```

Add mapping to the `apps.graphsrv` section pointing to the layout file.
```
apps:
  graphsrv:
    enabled: true
    layout_config_file: ./layout.yml
```



For more information, see graphsrv's documentation on the subject at <https://graphsrv.readthedocs.io/en/latest/custom/#layout>
