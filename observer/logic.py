# -*- mode:python; coding:utf-8; -*-
# created: 26.06.2010 22:56
# description: Observer logic 

from PyQt4 import QtGui, QtCore

from observer.network import Network

class FieldObject():
    """ Object on the field."""
    def __init__(self, image):
        """
        @type image: QtGui.QImage
        @param image: Sprite image.
        """
        self.__image = image

    def get_image(self):
        """
        @rtype:  QtGui.QImage
        @return: sprite of object.
        """
        return self.__image

    def set_image(self, image):
        """
        @type image:  QtGui.QImage
        @param image: sprite of object.
        """
        self.__image = image

class Player(FieldObject):
    """ Bot or human."""
    def __init__(self, image, name, bombs_count, bombs_radius):
        super(Player, self).__init__(self, image)

class Cell():
    """ One cell on the field."""
    def __init__(self, color, objects = []):
        self.__objects = objects
        self.__color = QtGui.QColor(255, 255, 255, 255)

    def add_objects(self, object):
        """
        @type objects:  GameObject.
        @param objects: Object to place at the sell.
        """
        self.__objects.append(object)
    
    def get_objects(self):
        """
        @rtype:  list
        @return: list of all objects at the sell
        """
        return self.__objects
    

    # property '__color' (QtGui.QColor)
    def set_color(self, color):
        """
        @type color:  QtGui.QColor  
        @param color: Color of sell.  
        """
        self.__color = color
    
    def get_color(self):
        """
        @rtype:  QtGui.QColor
        @return: Color of sell.
        """
        return self.__color

class Session():
    """ Contain information about current session."""
    __id = ""
    __game_types = []

    # property '__id' (str)
    def set_id(self, session_id):
        """
        @type session_id:  str  
        @param session_id: Session id returned by server in answer on handshake.
        """
        self.__session_id = session_id
    
    def get_id(self):
        """
        @rtype:  str
        @return: Session id returned by server in answer on handshake.
        """
        return self.__session_id
    
    # property '__game_types' (list)
    def set_game_types(self, game_types):
        """
        @type game_types:  list  
        @param game_types: List of game types avaliable on server.  
        """
        self.__game_types = game_types
    
    def get_game_types(self):
        """
        @rtype:  list
        @return: List of game types avaliable on server.
        """
        return self.__game_types
    
