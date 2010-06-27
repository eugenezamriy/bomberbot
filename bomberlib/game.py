# -*- mode:python; coding:utf-8; -*-
# created: 27.06.2010 11:47
# description: Bomberbot game process.


import random
import threading
import time

from bomberlib.player import Player
from bomberlib.logger import debug, error


BLANK, STONE, METAL = range(3)

__all__ = ["Game"]


class Game(threading.Thread):

    def __init__(self, game_id, game_data, out_queue, wait_timeout=30):
        """
        @type game_id:       unicode
        @param game_id:      Unique game ID.
        @type game_data:     dict
        @param game_data:    Game data dictionary. See db.GameType.as_dict() for details.
        @type out_queue:     Queue.Queue
        @param out_queue:    Game will put outgoing messages to this queue.
        @type wait_timeout:  int
        @param wait_timeout: Additional players waiting time in seconds.
        """
        threading.Thread.__init__(self, name="Game")
        self.__game_id = game_id
        self.__out_queue = out_queue
        self.__wait_timeout = wait_timeout
        self.__type_id = game_data["type_id"]
        self.__turn_time = game_data["turn_time"]           # milliseconds
        self.__init_bombs_count = game_data["init_bombs_count"]
        self.__max_bombx_count = game_data["max_bombs_count"]
        self.__init_bomb_radius = game_data["init_bomb_radius"]
        self.__bomb_delay = game_data["bomb_delay"]
        self.__min_players_count = game_data["min_players_count"]
        self.__max_players_count = game_data["max_players_count"]
        self.__map_name = game_data["map"]["name"]
        self.__map_height = game_data["map"]["height"]
        self.__map_width = game_data["map"]["width"]
        # generate map multidimensional array
        self.__map = [[BLANK for i in range(self.__map_width)] for i in range(self.__map_height)]
        if "stone" in game_data["map"]:
            for x, y in game_data["map"]["stone"]:
                self.__map[y][x] = STONE
        if "metal" in game_data["map"]:
            for x, y in game_data["map"]["metal"]:
                self.__map[y][x] = METAL
        self.__init_players_pos = []
        if "players" in game_data["map"]:
            for x, y in game_data["map"]["players"]:
                self.__init_players_pos.append((x, y))
        #
        self.__join_lock = threading.Lock()
        self.__game_runs = False
        self.__players = []

    def join_player(self, name, session_id, socket_id):
        """
        @type name:        unicode
        @param name:       Player name.
        @type session_id:  unicode
        @param session_id: Player session ID.
        @type socket_id:   int
        @param socket_id   Socket ID associated with player.

        @rtype: bool
        @return: Join status. True if player was joined to game.
        """
        if self.__join_lock.acquire(False):
            if len(self.__players) < self.__max_players_count and not self.__game_runs:
                self.__players.append(Player(name, session_id, socket_id))
                self.__join_lock.release()
                # launch game when minimal players count reached
                if len(self.__players) >= self.__min_players_count:
                    self.start()
                return True
            self.__join_lock.release()
        return False

    def run(self):
        debug("%s: game with id %s started" % (self, self.__game_id))
        # wait for additional players
        i = 0
        while len(self.__players) < self.__max_players_count and i < self.__wait_timeout:
            time.sleep(1)
            i += 1
        # begin game
        self.__join_lock.acquire()                # no more players can be joined to game
        self.__game_runs = True
        self.__align_players()                    # place players on inital positions
        # send starting message to all recipients
        j = {"status": "game_started",
             "game_id": self.__game_id,
             "turn_time": self.__turn_time,
             "map_width": self.__map_width,
             "map_height": self.__map_height,
             "players": map(lambda p: {p.name: [p.x, p.y]}, self.__players),
             "stone": self.__list_cells(STONE),
             "metal": self.__list_cells(METAL)}
        for player in self.__players:
            j["session_id"] = player.session_id
            self.__out_queue.put((player.socket_id, j), block=True, timeout=None)
        #
        while self.__game_runs:
            time.sleep(0.1)

    def __align_players(self):
        """Places players on initial positions."""
        def move_player(player, x, y):
            self.__map[y][x] = player
            player.x = x
            player.y = y
        free_positions = map(lambda p: p, self.__init_players_pos)
        free_players = map(lambda p: p, self.__players)
        # push players to predefined positions
        while free_positions != [] and free_players != []:
            player = free_players.pop()
            x, y = free_positions.pop()
            move_player(player, x, y)
        # push players to random free positions if needed
        for player in free_players:
            x, y = self.__find_random_cell(BLANK)
            if None in (x, y):
                raise Exception("critical server error: too many players in game")
            move_player(player, x, y)

    def __find_random_cell(self, cell_type):
        """Finds random cell with specified type."""
        cells = self.__list_cells(cell_type)
        return random.choice(cells) if len(cells) > 0 else (None, None)

    def __list_cells(self, cell_type):
        """Finds all cells with specified type."""
        cells = []
        for y in xrange(len(self.__map)):
            for x in xrange(len(self.__map[y])):
                if self.__map[y][x] == cell_type:
                    cells.append((x, y))
        return cells

    def __get_type_id(self):
        return self.__type_id

    type_id = property(__get_type_id)
