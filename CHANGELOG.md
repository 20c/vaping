
# Vaping Changes

## [Unreleased]
### Added
- fileprobe `backlog` config option
- fileprobe `max_lines` config option
- logparse allow custom validators
- logparse `validate_interval`
- logparse `time_parser config option
### Fixed
- fileprobe lines that can't be processed are now skipped
### Changed
- parse_interval now can handle multiunit strings such as 1m30s
### Deprecated
### Removed
### Security

## [1.1.0] 2018-12-05
### Added
- fileprobe plugin
- logparse plugin
- support for multiple output targets

### Fixed
- python3 encoding issue in the fping module


## [1.0.1] 2018-10-25
### Fixed
- ipv6 fping parsing #50


## [1.0.0]
### Added
- added graphite line protocol output plugin
- fping: exposed `period` parameter to config (Default to 20)
- error for using duplicate probe names

### Fixed
- update munge to reduce PyYAML requirements #35


## [0.6.1]
### Fixed
- issue where standalone vaping/vodka would not allow an fping probe to create more than one group


## [0.6.0]
### Added
- added python3.6 to tests
- add home_dir config option
- add better config testing
- add last time to fping
- add first iteration of mtr graph


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
