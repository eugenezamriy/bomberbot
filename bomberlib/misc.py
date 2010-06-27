# -*- mode:python; coding:utf-8; -*-
# created: 27.06.2010 11:52
# description: Miscellaneous bomberlib functions.


import datetime
import random


__all__ = ["generate_id"]


def generate_id():
    chars = map(lambda i: unicode(chr(i)), range(48, 58) + range(65, 91) + range(97, 123))
    td = datetime.datetime.now()
    # TODO: here 'll be a problem in 2062 year
    id_ = chars[int(str(td.year)[2:])] + chars[td.month] + chars[td.day] + chars[td.hour] + \
          chars[td.minute] + chars[td.second]
    while len(id_) < 10:
        id_ += random.choice(chars)
    return id_
