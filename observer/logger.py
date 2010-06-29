# created: 23.06.2010 21:44
# description: BomberBot logging module.


__all__ = ["debug", "error"]


import sys


def debug(message):
    sys.stdout.write("DEBUG: %s\n" % message)


def error(message):
    sys.stderr.write("ERROR: %s\n" % message)
