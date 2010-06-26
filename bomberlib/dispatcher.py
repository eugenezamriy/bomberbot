# -*- mode:python; coding:utf-8; -*-
# created: 26.06.2010 23:40
# description: Messages/games dispatching process.

# TODO: make JSON validator and remove validation from methods


import datetime
import threading
import random
import time
import Queue

import bomberlib.db as db
from bomberlib.errors import *
from bomberlib.logger import debug, error


class Dispatcher(threading.Thread):

    def __init__(self, in_queue, out_queue):
        threading.Thread.__init__(self, name="Dispatcher")
        self.__in_queue = in_queue
        self.__out_queue = out_queue

    def run(self):
        debug("%s: started" % self)
        while True:
            msg_found = False
            # incoming message processing
            try:
                j = None
                ts, socket_id, message = self.__in_queue.get(block=False)
                try:
                    if not message.has_key("cmd"):
                        raise BadCommandError()
                    elif message["cmd"] == "handshake":
                        j = self.__process_handshake(message)
                except BomberbotException, e:
                    j = generate_error(exception=e)
                except NotImplementedError, e:
                    j = generate_error(reason="this function not implemented yet")
                self.__send_message(socket_id, j)
                msg_found = True
            except Queue.Empty:
                pass
            # make some delay to avoid CPU eating
            if not msg_found:
                time.sleep(0.1)

    def __process_handshake(self, message):
        """Authenticates client on server and returns game types/games list if access allowed."""
        if "type" not in message or message["type"] not in ("observer", "player"):
            raise BadParamsError()
        if message["type"] == "observer":
            # TODO: must be implemented
            raise NotImplementedError()
        for f in ("email", "id"):
            if f not in message:
                raise BadParamsError()
        # TODO: authentication can be done with one join query
        user = db.session.query(db.User).filter_by(email=message["email"]).first()
        if user is None:
            raise AuthError()
        bot = db.session.query(db.Bot).filter_by(bot_id=message["id"]).filter_by(user_id=user.id).first()
        if bot is None:
            raise AuthError()
        session_id = self.__gen_session_id()
        j = {"status": "ok", "session_id": session_id}
        return j

    def __gen_session_id(self):
        # TODO: this generator copypasted from bot id generator
        # NOTE: don't know if collisions possible..? maybe add additional checking?
        chars = map(lambda i: unicode(chr(i)), range(48, 58) + range(65, 91) + range(97, 123))
        td = datetime.datetime.now()
        # TODO: here 'll be a problem in 2062 year
        id_ = chars[int(str(td.year)[2:])] + chars[td.month] + chars[td.day] + chars[td.hour] + \
              chars[td.minute] + chars[td.second]
        while len(id_) < 10:
            id_ += random.choice(chars)
        return id_

    def __send_message(self, socket_id, message):
        self.__out_queue.put((socket_id, message), block=True)
