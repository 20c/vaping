
from __future__ import absolute_import
from __future__ import print_function

import click
import munge
import munge.click

# test direct imports
import vaping
import vaping.daemon


class Context(munge.click.Context):
    app_name = 'vaping'
    config_class = vaping.Config


@click.group()
@click.version_option()
@Context.options
@Context.pass_context()
def cli(ctx, **kwargs):
    """
    Vaping
    """
    ctx.update_options(kwargs)


@cli.command()
@click.version_option()
@Context.options
@Context.pass_context()
@click.option('-d', '--no-fork', help='do not fork into background', is_flag=True, default=False)
def start(ctx, **kwargs):
    """
    start a vaping process
    """
    ctx.update_options(kwargs)

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
    start a vaping process
    """
    ctx.update_options(kwargs)

    daemon = vaping.daemon.Vaping(ctx.config)
    daemon.stop()

