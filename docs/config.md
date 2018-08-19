
## Introduction

Vaping will look for it's config directory in order of:

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

The `plugins` section is a list defining which plugins are loaded and possibly config to share between anything else referencing it. Each must define `type`, which can either be a plugin type, or the name of a previously defined type. To reference it later, `name` must be defined.

### fping

- `command` command to run
- `interval` time between pings
- `count` number of pings to send
- `period` time in milliseconds that fping waits between successive packets to an individual target

For example, the default of

```py
interval: 1m
count: 5
period: 20
```

sends 5 pings to each host every minute, with 20 milliseconds between each one.

## Probes

The `probes` section is a list defining input sections. It must define at least `type` which may refer directly to a plugin type, or to a config defined type.

## Custom Layouts

It is possible for you to add / edit your layouts, for more information see graphsrv's documentation on the subject at https://graphsrv.readthedocs.io/en/latest/custom/#layout
