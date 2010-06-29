# -*- mode:python; coding:utf-8; -*-
# created: 26.06.2010 22:56
# description: Observer logic 

from PyQt4 import QtGui, QtCore

from observer.network import Network

class FieldObject():
    """ Object on the field."""
    def __init__(self, path_to_sprite, pos = (0, 0)):
        """
        @type pos:             (int, int)
        @param pos:            position of object on the field.
        @type path_to_sprite:  str
        @param path_to_sprite: path to sprite image.
        """
        self.__image = QtGui.QImage(path_to_sprite)
        self.__x, self.__y = pos

    def get_pos(self):
        """
        @rtype:  (int, int)
        @return: position of object on the field.
        """
        return (self.__x, self.__y)

    def set_pos(self, pos):
        """
        @type pos:  (int, int)
        @param pos: position of object on the field.
        """
        self.__x, self.__y = pos
        self.get_image

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
    def __init__(self, path_to_sprite, pos = (0, 0)):
        FieldObject.__init__(self, path_to_sprite, pos)
        pass

class Cell():
    """ One cell on the field."""
    def __init__(self, size = 40, pos = (0, 0), object = None):
        self.__object = object
        self.__size = size
        self.__color = QtGui.QColor(255, 255, 255, 255)
        self.__x = 0
        self.__y = 0

    def set_size(self, size):
        """ Set cell size.

        @type size:  (int, int)
        @param size: Size of cell.
        """
        self.__x, self.__y = size

    def get_size(self):
        """ 
        @rtype:  tuple (int, int)
        @return: Size of cell.
        """
        return self.__size
    
    def set_pos(self, pos):
        self.__x, self.__y = pos

    def get_pos(self):
        return (self.__x, self.__y)

    def set_object(self, object):
        self.__object = object

    def get_object(self):
        return self.__object

    def set_color(self, color):
        self.__color = color

    def get_color(self):
        return self.__color
