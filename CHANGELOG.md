
# Vaping Changes

## [Unreleased]
### Added
- timeseries db abstraction plugin
- whisper db plugin
- RRDtool dn plugin

### Fixed
### Changed
### Deprecated
### Removed
### Security


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
