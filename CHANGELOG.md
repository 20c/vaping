
# Vaping Changes

## [Unreleased]
### Added
- added python3.6 to tests
- add home_dir config option

### Fixed
### Changed
### Deprecated
### Removed
### Security


## [0.5.0]
### Fixed
- issue #29: Python3 complains about bytes-like object in fping.py

### Changed
- port to pluginmgr .5
- updated other deps

## [0.4.0]
### Added
- timeseries db abstraction plugin
- whisper db plugin
- RRDtool db plugin

### Fixed
- pinned pluginmgr dependency to 0.4.0 as 0.5.0 currently breaks vaping


## [0.3.0]
### Added
- py3 support
- better startup failure messages
- check for plugin requirements (fping, zeromq)
- added on_start() and on_stop() events to plugins
- zeromq can connect or bind to socket

### Fixed
- #2 error if zeromq is missing
- #3 daemonize closes plugin fds

### Changed
- call start() on emit plugins
