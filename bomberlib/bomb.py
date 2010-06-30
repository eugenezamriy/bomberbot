# -*- mode:python; coding:utf-8; -*-
# created: 27.06.2010 13:15
# description: Bomberbot player representation.


class Bomb(object):

    def __init__(self, player, x, y, turn_placed, turn_detonated):
        """
        @type player:          Player
        @param player:         Player who placed this bomb.
        @type x:               int
        @param x:              X position.
        @type y:               int
        @param y:              Y position.
        @type turn_number:     int
        @param turn_number:    Bomb placement turn number.
        @type turn_detonated:  int
        @param turn_detonated: Bomb detonation turn number.
        """
        self.player = player
        self.x = x
        self.y = y
        self.turn_placed = turn_placed
        self.turn_detonated = turn_detonated
