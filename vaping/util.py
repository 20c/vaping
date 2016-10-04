# import to namespace
try:
    from shutil import which # noqa
except ImportError:
    from whichcraft import which # noqa
