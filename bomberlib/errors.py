# -*- mode:python; coding:utf-8; -*-
# created: 25.06.2010 22:28
# description: Contains all the exceptions and errors handling functions.


UNKNOWN_ERROR, BAD_CMD, BAD_PARAMS, AUTH_ERROR, SESSION_ERROR = range(5)

REASONS = {UNKNOWN_ERROR: "unknown server error",
           BAD_CMD: "wrong command received",
           BAD_PARAMS: "wrong command arguments",
           AUTH_ERROR: "invalid credentials",
           SESSION_ERROR: "seems your session was expired"}


class BomberbotException(Exception):

    def __init__(self, code, message=""):
        if message == "" and code in REASONS:
            message = REASONS[code]
        Exception.__init__(self, message)
        self.code = code
        self.message = message


class BadCommandError(BomberbotException):

    def __init__(self, message=""):
        BomberbotException.__init__(self, BAD_CMD, message)


class BadParamsError(BomberbotException):

    def __init__(self, message=""):
        BomberbotException.__init__(self, BAD_PARAMS, message)


class AuthError(BomberbotException):

    def __init__(self, message=""):
        BomberbotException.__init__(self, AUTH_ERROR, message)


class SessionError(BomberbotException):

    """Indicates wrong session id/session expiration."""

    def __init__(self, message=""):
        BomberbotException.__init__(self, SESSION_ERROR, message)


def generate_error(code=UNKNOWN_ERROR, reason="", exception=None):
    """ Returns dict {"status": "error", "reason": `reason`, "code": code}

        @type code:       int
        @param code:      Error code (optional).
        @type reason:     str
        @param reason:    Error reason (optional).
        @type exception:  Exception
        @param exception: Exception subclass with code/message arguments present (optional)."""
    # TODO: write better documentation for this function.
    j = {"status": "error", "code": code, "reason": reason}
    if exception is not None:
        j["reason"] = exception.message
        j["code"] = exception.code
    elif reason == "" and code in REASONS:
        j["reason"] = REASONS[code]
    return j
