# Changelog


## Unreleased
### Fixed
- added needed dependencies so gevent and other bits compile (thanks @seanknox)
### Removed
- python2.7 support
- python3.4 support
- python3.5 support


## 1.2.0
### Added
- python3.7 support
- fileprobe `backlog` config option
- fileprobe `max_lines` config option
- logparse allow custom validators
- logparse `validate_interval`
- logparse `time_parser` config option
- code documentation improvements
- pymdgen for apidocs
### Fixed
- fix startup issues with python 3.6+ and python2.7 on certain distributions
- mtr plugin py3 compatibility issues
- fileprobe lines that can't be processed are now skipped
- fix #62 timeseriesdb plugins crash when `update` is given `None` as a value
- fix #54 pytest > 3 for testing
### Changed
- update Dockerfile for smaller alpine build, add more options
- plugin groups can now be maintained under an explicit `groups` section in the plugin config (#44)
- move from `facsimile` to `ctl` for package / release management
- parse_interval now can handle multiunit strings such as 1m30s


## 1.1.0
### Added
- fileprobe plugin
- logparse plugin
- support for multiple output targets
### Fixed
- python3 encoding issue in the fping module


## 1.0.1
### Fixed
- ipv6 fping parsing #50


## 1.0.0
### Added
- added graphite line protocol output plugin
- fping: exposed `period` parameter to config (Default to 20)
- error for using duplicate probe names
### Fixed
- update munge to reduce PyYAML requirements #35


## 0.6.1
### Fixed
- issue where standalone vaping/vodka would not allow an fping probe to create more than one group


## 0.6.0
### Added
- added python3.6 to tests
- add home_dir config option
- add better config testing
- add last time to fping
- add first iteration of mtr graph


## 0.5.0
### Fixed
- issue #29: Python3 complains about bytes-like object in fping.py
### Changed
- port to pluginmgr .5
- updated other deps


## 0.4.0
### Added
- timeseries db abstraction plugin
- whisper db plugin
- RRDtool db plugin
### Fixed
- pinned pluginmgr dependency to 0.4.0 as 0.5.0 currently breaks vaping


## 0.3.0
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