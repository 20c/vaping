
# Change Log

## [Unreleased]
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

### Deprecated
### Removed
### Security

