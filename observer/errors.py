# -*- mode:python; coding:utf-8; -*-
# created: 26.06.2010 19:05
# description: Contain all exception classes

class WrongPacketError(Exception):
    """ Raises when server sends wrong formatted json."""
    pass

class NetworkError(Exception):
    """ Raises when some network error occures during sending packet"""
    pass
