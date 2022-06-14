## Customize Layout

Vaping allows users to customize its layout by supplying a new layout config file.

In the example below, the detail layout is changed to show 4 smokestack graphs instead of 3.

!!! Tip "Working directory matters for this example"
    To test example below, please execute the command from the vaping root
    directory. The example provides a relative path to the layout file and will not
    find it otherwise.

```sh
vaping start --home=examples/custom_layout --debug
```

### Configuration

To customize the layout, edit the default config from [graphsrv](https://github.com/20c/graphsrv/blob/master/graphsrv/etc/layouts.yaml) as needed.

For additional documentation on layout config attributes, please refer to the [graphsrv documentation](https://graphsrv.readthedocs.io/en/latest/custom/#layout) on the subject.

`examples/custom_layout/layouts.yaml`
```yml
{!examples/custom_layout/layouts.yaml!}
```

Then, specify a custom layout file should be loaded by setting the `apps.graphsrv.layout_config_file` config attribute in the vaping config.

`examples/custom_layout/config.yaml`
```yml
{!examples/custom_layout/config.yaml!}
```



