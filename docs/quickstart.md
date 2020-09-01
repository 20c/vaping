
## Install vaping

First, you will always need to install vaping with:

```sh
pip install vaping
```


!!! Tip "Error due to outdated setuptools"
    You may get an error when trying to install:

    error in vaping setup command: 'install_requires' must be a string or list of strings containing valid project/version requirement specifiers; Expected ',' or end-of-list in whichcraft==0.4.0 ; python_version<'3.3' at  ; python_version<'3.3'

    This means you need to update your setuptools, you can do so by running

    ```
    pip install setuptools -U
    ```

### Install fping

Most examples require `fping` to be installed.

To install for CentOS or RHEL, you can get the package from EPEL:

```sh
yum install epel-release
yum install fping
```

To install for Debian Or Ubuntu:

```sh
sudo apt-get install fping
```


## Example Standalone Latency

The example config file (from `examples/standalone_dns`) uses both vodka and graphsrv plugins, so those will need to be installed with:

```sh
pip install -U vodka
pip install -U graphsrv
```

!!! Tip "You can still use old graphsrv"
    We have recently added a major upgrade to graphsrv by switching to a d3.js based frontend.

    While this upgrade should be seamless on your end, if you still want to use the old graphsrv for now you can do so by pinning the version to 1.2.0

    ```
    pip install graphsrv==1.2.0
    ```

Then just start vaping with:

```sh
vaping start --home=examples/standalone_dns/ --debug
```

By default it uses a generic layout template and listens on http://0.0.0.0:7021 - going to that in a browser should produce the summary paging which looks like:

![Vaping](https://raw.githubusercontent.com/20c/vaping/master/docs/img/standalone_dns.png)

And clicking on the title will goto a detail page which looks like:

![Vaping](https://raw.githubusercontent.com/20c/vaping/master/docs/img/standalone_dns-detail.png)

Below is the config file, common things to change include:

- hosts: probes.public_dns.hosts
- listening address: plugins.vodka.plugins.http.host and port.
- fping frequency: plugins.std_fping.count and interval

Config file:

`examples/standalone_dns/config.yml`:
```yml
{!examples/standalone_dns/config.yml!}
```


## Example Distributed Latency

The example config file (from `examples/distributed_dns`) is the same as the standalone one and uses both vodka and graphsrv, so those will need to be installed with:

```sh
pip install -U vodka
pip install -U graphsrv
```

The main difference is the collector is running in a separate process than the
web server, which allows you to graph things from multiple locations, as well
as using another webserver, such as nginx to serve client requests.


To try it out, start vaping with:

```sh
vaping start --home=examples/distributed_dns/vaping/ --debug
```

### Gunicorn

To test with gunicorn, first install it:

```sh
pip install gunicorn
```

plugins['http'].server is already set to 'gunicorn' in
`examples/distributed_dns/vodka/config.yml` so run:

```sh
export VODKA_HOME=examples/distributed_dns/vodka
gunicorn -b 0.0.0.0:7021 vodka.runners.wsgi:application
```

You should be able to browse to port 7021 to see the display.

#### Gunicorn fails to start

If gunicorn fails to start and doesn't tell you why, its probably some missing
dependency. You can force it to output what it is failing on by passing the
`--preload` argument to the `gunicorn` command.

### nginx

To test with nginx, install uwsgi:

```sh
pip install uwsgi
```

In `examples/distributed_dns/vodka/config.yml` change plugins['http'].server
to 'uwsgi' and then configure nginx with an upstream to connect to it.

`nginx.conf`:
```
upstream vaping {
    server 127.0.0.1:7021;
}
```

Start the uwsgi process with:

```sh
export VODKA_HOME=examples/distributed_dns/vodka
uwsgi -H $VIRTUAL_ENV --socket=0.0.0.0:7026 -w vodka.runners.wsgi:application --enable-threads
```

And you should be able to point your browser to the address nginx is listening
on to view it.

!!! Tip "Note"
    If you're running selinux, you'll need to allow nginx to connect to it
    with `setsebool -P httpd_can_network_connect 1`.

Config files:

`examples/distributed_dns/vaping/config.yml`:
```yml
{!examples/distributed_dns/vaping/config.yml!}
```

`examples/distributed_dns/vodka/config.yml`:
```yml
{!examples/distributed_dns/vodka/config.yml!}
```

## Deep dive into the distributed example

Looking at https://github.com/20c/vaping/tree/master/examples/distributed_dns

There are two directories in there, one called `vodka` and one called `vaping`

`vodka` is the config that is used by the vodka web service (so this would be your web server)
`vaping` is the config that is used by a vaping process that runs and fping and send the data to `vodka`

While for the standalone variation vaping can run vodka as a plugin, in this case both are meant to 
be run in separate processes and can be on separate hosts.

Going by the example to start the web server on one host (using gunicorn to run it):

```
export VODKA_HOME=examples/distributed_dns/vodka
gunicorn -b 0.0.0.0:7021 vodka.runners.wsgi:application
```

And then start the vaping that runs fping on a different host:

```
vaping start --home=examples/distributed_dns/vaping/ --debug
```

## Configuring zmq and groups

### Vodka (web server)

In the vodka config each zeromq connection is instantiated by the `zeromq_probe` plugin, so it needs one of those for each vaping sending data.  Please be aware of https://github.com/20c/vodka/issues/11 since it's a bit counterintuitive at this point in time.

```
plugins:
  ...
  # zero mq probe plugin (latency name is important, so it can be
  # routed properly to the similarly named group)
  - name: latency
    type: zeromq_probe
    data: fping
    interval: 1.0
    bind: tcp://127.0.0.1:6021
    async: thread
```

Additionally vodka will need to be made aware of any data group that will be sent to it, so each new vaping process will need a new group added in `apps.graphsrv.groups`

```
apps:
  graphsrv:
    groups:
      # same name as zeromq_probe instance name above (important!)
      latency:
        public_dns:
          8.8.8.8:
            name: Google DNS
            color: red
          4.2.2.1:
            name: Level(3)
            color: blue
          208.67.222.222:
            name: OpenDNS
            color: orange
```

### Vaping

Likewise in the vaping config you will need to configure the zmq connection via the `zeromq` plugin

```
plugins:
  ...
  - name: zmq_vodka
    type: zeromq
    bind: tcp://127.0.0.1:6021
```
