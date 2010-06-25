# -*- mode:python; coding:utf-8; -*-
# created: 25.06.2010 22:28
# description: Contain all the exceptions and error handling functions.

def generate_error(reason):
    """ Return dict {"status": "error", "reason": `reason`}

        @type reason:  str
        @param reason: Error reason."""
    return {"status": "error", "reason": reason}
