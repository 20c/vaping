
# Vaping

[![PyPI](https://img.shields.io/pypi/v/vaping.svg?maxAge=60)](https://pypi.python.org/pypi/vaping)
[![PyPI](https://img.shields.io/pypi/pyversions/vaping.svg?maxAge=600)](https://pypi.python.org/pypi/vaping)
[![Tests](https://github.com/20c/vaping/workflows/tests/badge.svg)](https://github.com/20c/vaping)
[![LGTM Grade](https://img.shields.io/lgtm/grade/python/github/20c/vaping)](https://lgtm.com/projects/g/20c/vaping/alerts/)
[![Codecov](https://img.shields.io/codecov/c/github/20c/vaping/master.svg)](https://codecov.io/github/20c/vaping)


vaping is a healthy alternative to smokeping!*

* (This statement has not been evaluated by the Food and Drug Administration)

![Vaping](https://raw.githubusercontent.com/20c/vaping/master/docs/img/vaping.png)

## Introduction

Vaping provides the following features:

- Real-time latency graphing viewable in the browser
- Line and smokestack graphs
- Containerized and easy to setup and configure
- Support for time-series databases
- Plugin-based design to allow integration with other services
- Supports distributed setups through message queue

Vaping is a Python daemon which polls for input and sends its output through plugins.

It has a standalone mode to directly serve realtime graphs in a browser, or can use ZeroMQ to distribute messages.

## Installation

```sh
pip install vaping
```

You will need a compiler and Python development libraries for some components, which you can obtain with the `gcc` and `python-devel` packages for your operating system.

Alternatively, you can use the [Docker image](Dockerfile), which includes all requirements.

## Quick Start

To use Vaping, you need first a configuration file that defines which hosts to target and where to send the output. You can have a look at [the examples in this repository](examples/) and adapt them to your needs.

Then, start the `vaping` program from the command line, specifying the path to the configuration file.

A quick start example is [available here](https://vaping.readthedocs.io/en/stable/quickstart/). It shows you how to ping multiple hosts and display the resulting graphs using a local web server.

## Usage


Vaping has a command-line interface with the following usage:

```
Usage: vaping [OPTIONS] COMMAND [ARGS]...

  Vaping

Options:
  --version    Show the version and exit.
  --quiet      no output at all
  --verbose    enable more verbose output
  --home TEXT  specify the home directory, by default will check in order:
               $VAPING_HOME, ./.vaping, ~/.config/vaping
  --debug      enable extra debug output
  --help       Show this message and exit.

Commands:
  start    start a vaping process
  stop     stop a vaping process
  restart  restart a vaping process
```

### start

Starts a vaping process, by default will fork into the background unless
`--debug` or `--no-fork` is passed.

It adds options:

```
  -d, --no-fork  do not fork into background
```


### stop

Stops a vaping process identified by `$VAPING_HOME/vaping.pid`


## Documentation

Documentation is created with mkdocs and available here:

**stable**: <http://vaping.readthedocs.io/en/stable/>

**latest**: <http://vaping.readthedocs.io/en/latest/>


## Changes

The current change log is available at <https://github.com/20c/vaping/blob/master/CHANGELOG.md>


## License

Copyright 2016-2021 20C, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

