## Two distributed vaping instances into the same graph

This example shows how two run 2 separate vaping instances connected to a vodka instance and plot into the same graph.

!!! Tip "Running a distributed setup"
    For a complete understanding of running a distributed vaping setup, please read the [Distributed Latency](quickstart/#example-distributed-latency) example in the quickstart section.

!!! Tip "Requires vodka 2.2.6"
    This requires that you install vodka 2.2.6 or higher

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
