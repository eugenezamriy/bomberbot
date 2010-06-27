# -*- mode:python; coding:utf-8; -*-
# created: 20.06.2010 23:08
# description: Bomberbot database related stuff.


import datetime
import hashlib
try:
    import json
except ImportError:
    import simplejson as json
import random
from sqlalchemy import Column, ForeignKey, Integer, Table, MetaData, Unicode, UnicodeText
import sqlalchemy.engine
import sqlalchemy.orm as orm


__all__ = ["init_db", "games_table", "users_table", "bots_table", "maps_table", "engine", "meta",
           "session", "GameType", "User", "Bot", "Map"]


meta = MetaData()

engine = None

session = None


users_table = Table("users", meta,
                    Column("id", Integer, autoincrement=True, primary_key=True),
                    Column("email", Unicode(50), nullable=False, unique=True),
                    Column("login", Unicode(25), nullable=False, unique=True),
                    # md5sum hexdigest
                    Column("password", Unicode(32), nullable=False))


bots_table = Table("bots", meta,
                   Column("id", Integer, autoincrement=True, primary_key=True),
                   Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                   # random generated bot ID
                   Column("bot_id", Unicode(10), nullable=False, unique=True),
                   Column("name", Unicode(25), nullable=False, unique=True))


game_types_table = Table("game_types", meta,
                         Column("id", Integer, autoincrement=True, primary_key=True),
                         # game type id, unique string defined by administrator
                         Column("type_id", UnicodeText, nullable=False, unique=True),
                         Column("map_id", Integer, ForeignKey("maps.id"), nullable=False),
                         # one turn time in milliseconds
                         Column("turn_time", Integer, default=5000, nullable=False),
                         Column("init_bombs_count", Integer, default=1, nullable=False),
                         Column("max_bombs_count", Integer, default=5, nullable=False),
                         Column("init_bomb_radius", Integer, default=1, nullable=False),
                         # bomb detonation delay in turns
                         Column("bomb_delay", Integer, default=4, nullable=False),
                         Column("min_players_count", Integer, default=2, nullable=False),
                         Column("max_players_count", Integer, default=4, nullable=False))


maps_table = Table("maps", meta,
                   Column("id", Integer, autoincrement=True, primary_key=True),
                   Column("name", Unicode(20), nullable=False, unique=True),
                   Column("height", Integer, nullable=False),
                   Column("width", Integer, nullable=False),
                   # json encoded map data
                   Column("data", UnicodeText, nullable=False))


class User(object):

    def __init__(self, email, login, password):
        """
        @type email:     unicode
        @param email:    User e-mail address.
        @type login:     unicode
        @param login:    User login.
        @type password:  unicode
        @param password: User password (will be converted to md5 hexdigest internally).
        """
        self.email = email
        self.login = login
        self.password = unicode(hashlib.md5(password).hexdigest())

    def __repr__(self):
        return u"<User('%s','%s','%s')>" % (self.id, self.email, self.login)


class Bot(object):

    def __init__(self, name, id_=None):
        """
        @type name:  unicode
        @param name: Bot name.
        """
        # TODO: id_ parameter must be removed in production code
        self.name = name
        self.bot_id = self.__gen_bot_id() if id_ is None else id_

    def __gen_bot_id(self):
        """
        Generates random bot ID.

        @rtype:  unicode
        @return: Random bot ID.
        """
        chars = map(lambda i: unicode(chr(i)), range(48, 58) + range(65, 91) + range(97, 123))
        td = datetime.datetime.now()
        # TODO: here 'll be a problem in 2062 year
        id_ = chars[int(str(td.year)[2:])] + chars[td.month] + chars[td.day] + chars[td.hour] + \
              chars[td.minute] + chars[td.second]
        while len(id_) < 10:
            id_ += random.choice(chars)
        return id_

    def __repr__(self):
        return u"<Bot('%s','%s','%s')>" % (self.id, self.user_id, self.name)


class GameType(object):

    def __init__(self, type_id):
        self.type_id = type_id

    def as_dict(self):
        """Creates dictionary from data in db."""
        j = {"map": {}}
        for f in ("type_id", "turn_time", "init_bombs_count", "max_bombs_count", "init_bomb_radius",
                  "bomb_delay", "min_players_count", "max_players_count"):
            j[f] = getattr(self, f)
        for f in ("height", "name", "width"):
            j["map"][f] = getattr(self.map, f)
        data = json.loads(self.map.data)
        for f in ("players", "stone", "metal"):
            j["map"][f] = data[f] if data.has_key(f) else []
        return j

    def __repr__(self):
        return u"<Game('%s','%s','%s')>" % (self.id, self.type_id, self.map_id)


class Map(object):

    def __init__(self, name, height, width, data):
        """
        @type name:  unicode
        @param name: Map name.
        @type data:  unicode
        @param data: Json encoded map data.
        """
        self.name = name
        self.height = height
        self.width = width
        self.data = data

    def __repr__(self):
        return u"<Map('%s','%s')>" % (self.id, self.name)


orm.mapper(User, users_table, properties={
    "bots": orm.relation(Bot, backref="user")
    })

orm.mapper(Bot, bots_table)

orm.mapper(GameType, game_types_table)

orm.mapper(Map, maps_table, properties={
    "game_types": orm.relation(GameType, backref="map")
    })


def init_db(db_string, debug=False):
    """
    Creates database connection (and database itself if needed).

    @type db_string:   str
    @param db_string:  Database connection string. See SQLAlchemy documentation for details.
    @type debug:       bool
    @param debug:      If True enables logging of all statements to console (False by default).
    """
    global engine, meta, session
    engine = sqlalchemy.engine.create_engine(db_string, echo=debug)
    meta.bind = engine
    meta.create_all(checkfirst=True)
    # TODO: doublecheck sqlalchemy documentaion about this
    sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=True)
    session = orm.scoped_session(sm)
    # populate database with test data
    user = User(u"test@example.com", u"test", u"test")
    session.add(user)
    bot1 = Bot(u"test_bot1", u"test_id1")
    bot2 = Bot(u"test_bot2", u"test_id2")
    user.bots.append(bot1)
    user.bots.append(bot2)
    #
    map_ = Map(u"dynablaster", 11, 13, u'{"players": [[0, 0], [12, 0], [0, 10], [12, 10]], "stone": [[2, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [2, 1], [6, 1], [0, 2], [1, 2], [2, 2], [4, 2], [7, 2], [8, 2], [9, 2], [10, 2], [11, 2], [12, 2], [2, 3], [4, 3], [8, 3], [10, 3], [12, 3], [0, 4], [2, 4], [3, 4], [4, 4], [5, 4], [8, 4], [9, 4], [10, 4], [11, 4], [12, 4], [0, 5], [2, 5], [4, 5], [6, 5], [8, 5], [10, 5], [12, 5], [0, 6], [1, 6], [2, 6], [3, 6], [4, 6], [6, 6], [8, 6], [9, 6], [10, 6], [11, 6], [12, 6], [0, 7], [4, 7], [6, 7], [10, 7], [12, 7], [0, 8], [1, 8], [2, 8], [3, 8], [5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [11, 8], [12, 8], [2, 9], [10, 9], [2, 10], [3, 10], [4, 10], [5, 10], [6, 10], [9, 10], [10, 10]], "metal": [[1, 1], [3, 1], [5, 1], [7, 1], [9, 1], [11, 1], [1, 3], [3, 3], [5, 3], [7, 3], [9, 3], [11, 3], [1, 5], [3, 5], [5, 5], [7, 5], [9, 5], [11, 5], [1, 7], [3, 7], [5, 7], [7, 7], [9, 7], [11, 7], [1, 9], [3, 9], [5, 9], [7, 9], [9, 9], [11, 9]]}')
    game_type = GameType(u"2-4_deathmatch")
    game_type.map = map_
    session.add(map_)
    session.commit()
