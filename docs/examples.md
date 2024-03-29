## Two distributed vaping instances on the same graph

This example shows how two run 2 separate vaping instances connected to a vodka instance and plot on the same graph.

!!! Tip "Running a distributed setup"
    For a complete understanding of running a distributed vaping setup, please read the [Distributed Latency](/docs/quickstart) example in the quickstart section.

!!! Tip "Requires vodka 2.2.6"
    This requires that you install vodka 2.2.6 or higher:

    ```
    pip install vodka>=2.2.6
    ```

**Vaping instance 1 - this one will ping 1.1.1.1**

`examples/distributed_shared_graph/vaping-1/config.yml`:
```yml
{!examples/distributed_shared_graph/vaping-1/config.yml!}
```

```sh
vaping start --home=examples/distributed_shared_graph/vaping-1 --debug
```

**Vaping instance 2 - this one will ping 8.8.8.8**

`examples/distributed_shared_graph/vaping-2/config.yml`:
```yml
{!examples/distributed_shared_graph/vaping-2/config.yml!}
```

```sh
vaping start --home=examples/distributed_shared_graph/vaping-2 --debug
```

**Vodka**

`examples/distributed_shared_graph/vodka/config.yml`:
```yml
{!examples/distributed_shared_graph/vodka/config.yml!}
```

```sh
export VODKA_HOME=examples/distributed_shared_graph/vodka
gunicorn -b 0.0.0.0:7021 vodka.runners.wsgi:application
```

## MTR

This example will show you how to setup an MTR graph:

!!! Tip "Requires graphsrv 1.3.0"

    You need to run graphsrv 1.3.0 or later in order to be able
    to render MTR graphs.

    ```
    pip install graphsrv>=1.3.0
    ```

!!! Tip "Requires traceroute"

    We use the `traceroute` command to determine the hops to
    send to fping. Make sure it is installed.


!!! Tip "MTR Graph is currently experimental"

    The MTR graph is introduced to vaping in version 0.6.0 and should
    be considered an early iteration of MTR data visualization to vaping.

    We have ideas on how to make it better, but would also love to hear your
    thoughts on it.


Pay close attention to the commented lines in the example below, as you need to do the following:

- setup the mtr probe
- setup the fping_mtr plugin
- setup the fping_mtr data type
- setup the mtr graph


`examples/mtr/config.yml`:
```yml
{!examples/mtr/config.yml!}
```

```sh
vaping start --home=examples/mtr --debug
```

!!! Tip "MTR - Distributed"

    When setting up a distributed MTR probe, the group on the vodka end should be setup like this:

        apps:
          graphsrv:
            enabled: true

            groups:
              mtr:
                config:
                  default_graph: mtr
                cloudflare_dns:
                  1.1.1.1:
                    name: Cloudflare
                    color: mediumpurple
