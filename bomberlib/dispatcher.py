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
from bomberlib.game import Game
from bomberlib.logger import debug, error
from bomberlib.misc import generate_id


__all__ = ["Dispatcher"]

PLAYER, OBSERVER = range(2)

#: termporary session ids deletion interval (in seconds)
TMP_SIDS_TIMEOUT = 1800


class Dispatcher(threading.Thread):

    def __init__(self, in_queue, out_queue):
        threading.Thread.__init__(self, name="Dispatcher")
        self.__in_queue = in_queue
        self.__out_queue = out_queue
        # temporary session ids storage: session id = (type, timestamp in seconds)
        # records older then TMP_SIDS_TIMEOUT seconds 'll be deleted
        self.__tmp_sids = {}
        # games storage: game_id = game object
        self.__games = {}

    def run(self):
        debug("%s: started" % self)
        while True:
            # TODO: delete old temporary session id's
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
                    elif message["cmd"] == "join":
                        self.__process_join(message, socket_id)
                except BomberbotException, e:
                    j = generate_error(exception=e)
                except NotImplementedError, e:
                    j = generate_error(reason="this function not implemented yet")
                #except Exception, e:
                #    # TODO: advanced debug information must be logged here
                #    j = generate_error(reason=str(e))
                if j is not None:
                    self.__send_message(socket_id, j)
                msg_found = True
            except Queue.Empty:
                pass
            # make some delay to avoid CPU eating
            if not msg_found:
                time.sleep(0.1)

    def __process_join(self, message, socket_id):
        """
        Adds player/observer to free game or creates new game.

        @type message:    dict
        @param message:   Incoming message dictionary.
        @type socket_id:  int
        @param socket_id: Socket ID associated with this player/observer.
        """
        if "session_id" not in message or "type_id" not in message:
            raise BadParamsError()
        session_id = message["session_id"]
        if session_id not in self.__tmp_sids:
            raise SessionError()
        if self.__tmp_sids[session_id][0] != PLAYER:
            raise NotImplementedError()
        #
        type_id = message["type_id"].strip()
        gt = db.session.query(db.GameType).filter_by(type_id=type_id).first()
        if not gt:
            raise BadParamsError("unknown game type %s" % type_id)
        # find free game for player
        player_name = self.__tmp_sids[session_id][1]
        joined = False
        for game_id in self.__games:
            game = self.__games[game_id]
            if game.type_id == type_id:
                joined = game.join_player(player_name, session_id, socket_id)
                break
        if not joined:
            # no free games found - create new one
            game_id = generate_id()
            while game_id in self.__games:
                game_id = generate_id()
            game = Game(game_id, gt.as_dict(), self.__out_queue)
            self.__games[game_id] = game
            if not game.join_player(player_name, session_id, socket_id):
                raise Exception("Critical server error: can't join fresh created game")
        # remove session ID from temporary storage. Now it part of game.
        self.__tmp_sids.pop(session_id)

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
        #
        session_id = generate_id()
        while session_id in self.__tmp_sids:
            session_id = generate_id()
        #
        j = {"status": "ok", "session_id": session_id, "game_types": self.__make_game_types_list()}
        self.__tmp_sids[session_id] = (PLAYER, bot.name, time.time())
        return j

    def __make_game_types_list(self):
        types = []
        for gt in db.session.query(db.GameType).all():
            j = {}
            for f in ("type_id", "turn_time", "init_bombs_count", "max_bombs_count",
                      "init_bomb_radius", "bomb_delay", "min_players_count", "max_players_count"):
                j[f] = getattr(gt, f)
            for f in ("name", "height", "width"):
                j["map_" + f] = getattr(gt.map, f)
            types.append(j)
        return types

    def __send_message(self, socket_id, message):
        self.__out_queue.put((socket_id, message), block=True)
