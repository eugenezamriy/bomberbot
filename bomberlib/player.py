# -*- mode:python; coding:utf-8; -*-
# created: 27.06.2010 13:15
# description: Bomberbot player representation.


class Player(object):

    def __init__(self, name, session_id, socket_id):
        self.__name = name
        self.__session_id = session_id
        self.socket_id = socket_id
        # player coordinates on game field
        self.x = None
        self.y = None

    def __get_name(self):
        return self.__name

    def __get_session_id(self):
        return self.__session_id

    name = property(__get_name)

    session_id = property(__get_session_id)
