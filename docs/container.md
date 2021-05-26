
# Vaping Dockerfile

The base `Dockerfile` will build an alpine image containing:

- a python 3.7 virtual environment containing vaping at `/venv/`
- the vaping examples at `/app/examples`


## To build the image

### Build args

- `dep_packages` - OS packages to install (default: `fping`)
- `virtual_env` - What image directory to install the virtual env into (default: `/venv`)
- `vaping_home` - What vaping should use as a `--home` directory (default: `/app/examples/standalone_dns`)
- `vaping_uid` - What user id to run vaping as (default: `1000`)

```sh
docker build -t vaping:$(cat Ctl/VERSION) --build-arg=vaping_uid=1002 .
```


## To run the image

### Environment variables

- `VAPING_HOME` - What vaping should use as a `--home` directory

### Docker command

By default, it exposes port 7021, so:

```sh
docker run -p 7021:7021 -it --rm vaping:$(cat Ctl/VERSION)
```
