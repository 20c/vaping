
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


## Probes

The `probes` section is a list defining input sections. It must define at least `type` which may refer directly to a plugin type, or to a config defined type.

