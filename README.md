
# Vaping

[![PyPI](https://img.shields.io/pypi/v/vaping.svg?maxAge=3600)](https://pypi.python.org/pypi/vaping)
[![PyPI](https://img.shields.io/pypi/pyversions/vaping.svg?maxAge=3600)](https://pypi.python.org/pypi/vaping)
[![Travis CI](https://img.shields.io/travis/20c/vaping.svg?maxAge=3600)](https://travis-ci.org/20c/vaping)
[![Codecov](https://img.shields.io/codecov/c/github/20c/vaping/master.svg?maxAge=3600)](https://codecov.io/github/20c/vaping)
[![Requires.io](https://img.shields.io/requires/github/20c/vaping.svg?maxAge=3600)](https://requires.io/github/20c/vaping/requirements)

vaping is a healthy alternative to smokeping!

![Vaping](https://raw.githubusercontent.com/20c/vaping/master/docs/img/vaping.png)

## Introduction

Vaping was started after years of frustation from dealing with perl and
environment management for smokeping. It's a simple python daemon which uses
green threads to poll for input and send output through plugins.

It has a standalone mode to directly serve realtime graphs, or can use ZeroMQ
to distribute.


## Installation

```sh
pip install vaping
```

Note, you will need a compiler and python development libraries for some components.

On CentOS/RHEL:

```sh
yum install gcc python-devel
```


## Usage

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

Copyright 2016-2019 20C, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this softare except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

