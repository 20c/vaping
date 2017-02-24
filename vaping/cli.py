
from __future__ import absolute_import
from __future__ import print_function

import click
import munge
import munge.click
import os

# test direct imports
import vaping
import vaping.daemon


class Context(munge.click.Context):
    app_name = 'vaping'
    config_class = vaping.Config


def update_context(ctx, kwargs):
    ctx.update_options(kwargs)

    if not isinstance(ctx.config['vaping']['plugin_path'], list):
        raise ValueError('config item vaping.plugin_path must be a list')
    # set plugin search path to defined + home/plugins
    searchpath = ctx.config['vaping']['plugin_path']
    if ctx.home:
        searchpath.append(os.path.join(ctx.home, 'plugins'))
    vaping.plugin.searchpath = searchpath


@click.group()
@click.version_option()
@Context.options
@Context.pass_context()
def cli(ctx, **kwargs):
    """
    Vaping
    """
    update_context(ctx, kwargs)


@cli.command()
@click.version_option()
@Context.options
@Context.pass_context()
@click.option('-d', '--no-fork', help='do not fork into background', is_flag=True, default=False)
def start(ctx, **kwargs):
    """
    start a vaping process
    """
    update_context(ctx, kwargs)

    daemon = vaping.daemon.Vaping(ctx.config)

    if ctx.debug or kwargs['no_fork']:
        daemon.run()
    else:
        daemon.start()


@cli.command()
@click.version_option()
@Context.options
@Context.pass_context()
def stop(ctx, **kwargs):
    """
    stop a vaping process
    """
    update_context(ctx, kwargs)

    daemon = vaping.daemon.Vaping(ctx.config)
    daemon.stop()


@cli.command()
@click.version_option()
@Context.options
@Context.pass_context()
def restart(ctx, **kwargs):
    """
    restart a vaping process
    """
    update_context(ctx, kwargs)

    daemon = vaping.daemon.Vaping(ctx.config)
    daemon.stop()
    daemon.start()

