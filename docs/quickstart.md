
## Install vaping

First, you will always need to install vaping with:

```sh
pip install vaping
```

## Example Standalone Latency

The example config file (from `examples/standalone_dns`) uses both vodka and graphsrv plugins, so those will need to be installed with:

```sh
pip install vodka
pip install graphsrv
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

```yml
{!examples/standalone_dns/config.yml!}
```
