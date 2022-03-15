## Customize Layout

Vaping allows you to customize your layout by supplying a new layout config file.

In the example below we change the detail layout to show 4 smokestack graphs instead 3.

!!! Tip "Working directory matters for this example"
    If you want to try the example below please execute the command from the vaping root
    directory. The example provides a relative path to the layout file and will not
    find it otherwise.

```sh
vaping start --home=examples/custom_layout --debug
```

### Configuration

To customize your layout, take the default config from [graphsrv](https://github.com/20c/graphsrv/blob/master/graphsrv/etc/layouts.yaml) and edit it to meet your needs.

For additional documentation on layout config attributes please refer to the [graphsrv documentation](https://graphsrv.readthedocs.io/en/latest/custom/#layout) on the subject.

`examples/custom_layout/layouts.yaml`
```yml
{!examples/custom_layout/layouts.yaml!}
```

Then specify that you want to load a custom layout file by setting the `apps.graphsrv.layout_config_file` config attribute in your vaping config.

`examples/custom_layout/config.yaml`
```yml
{!examples/custom_layout/config.yaml!}
```



