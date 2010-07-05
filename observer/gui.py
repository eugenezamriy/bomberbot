# -*- mode:python; coding:utf-8; -*-
# created: 27.06.2010 12:19
# description: GUI part of observer

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui import QColor, QImage

from observer.network import Network
from observer.logic import *
from observer.errors import NetworkError
from observer.misc import TableModel

form_class, base_class = uic.loadUiType("observer/enter_window.ui")

session = Session()

class EnterWindow(QtGui.QWidget, form_class):

    network = None
    __selected_row = []

    def __init__(self, *args):
        super(EnterWindow, self).__init__(*args)
        self.setupUi(self)

        self.__settings = QSettings(self)
        self.__server = str(self.__settings.value("server", 
            "localhost:41000").toString())
        self.__email = str(self.__settings.value("email", 
            "test@example.com").toString())
        self.__user_id = str(self.__settings.value("id", 
            "test_id1").toString())

        self.id_edit.setText(self.__user_id)
        self.email_edit.setText(self.__email)
        self.server_edit.setText(self.__server)

        self.save_info_button.setEnabled(False)
        self.setWindowTitle("Bomberbot client")
        self.setLayout(self.main_layout)

    # logic

    @QtCore.pyqtSlot('PyQt_PyObject')
    def on_handshake_complete(self, message):
        global session
        session.set_id(message["session_id"])
        session.set_game_types(message["game_types"])

        if len(message["game_types"]) > 0:
            headers = ["Game Type", 
                       "Init Bombs Count", 
                       "Max Players Count",
                       "Field Size"]
            data = [[x["type_id"], 
                     x["init_bombs_count"], 
                     x["max_players_count"],
                     str(x["map_height"]) + "x" + str(x["map_width"])] 
                     for x in message["game_types"]]
            self.games_table.setModel(TableModel(data, headers, self))
            self.games_table.resizeColumnsToContents()

            self.__sel_model = self.games_table.selectionModel()
            self.__sel_model.selectionChanged.connect(self.on_game_selected)
        else:
            self.__show_error("No started games found. Try again later.")

    # gui event handlers

    @QtCore.pyqtSlot()
    def on_connect_button_clicked(self):
        """ Called every time when user clicks connect_button."""
        host, port = "", 0
        server_address = str(self.server_edit.text())
        # Validate server_address and divide it into host and port.
        # TODO: Add more validation.
        delim_pos = server_address.find(":")
        if delim_pos != -1:
            host = server_address[:delim_pos]
            port = int(server_address[delim_pos + 1:])
        if delim_pos == -1 or host == "" or port == 0:
            self.__show_error("Wrong server address. Please enter a right one.")
            return 

        if self.network:
            if self.network.isRunning():
                self.network.terminate()
        else:
            self.network = Network(host, port)
            self.network.handshake_complete.connect(self.on_handshake_complete)

        self.network.start()

        p = {"cmd"  : "handshake",
             "email": self.__email,
             "id"   : self.__user_id,
             "type" : "player"}
        self.network.send(p)

    @QtCore.pyqtSlot()
    def on_join_button_clicked(self):
        global session
        session_id = session.get_id()
        game_types = session.get_game_types()


        current_row = self.__sel_model.selectedRows()[0].row()
        game = game_types[current_row]
        self.__wait_window = WaitWindow(self)
        self.__wait_window.show()

        p = {"cmd"       : "join",
             "session_id": session_id,
             "type_id"   : game["type_id"]}

        self.network.send(p)
        self.hide()

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_game_selected(self, selected, deselected):
        self.join_button.setEnabled(True)

    @QtCore.pyqtSlot(str)
    def on_email_edit_textChanged(self, text):
        self.save_info_button.setEnabled(True)

    @QtCore.pyqtSlot(str)
    def on_id_edit_textChanged(self, text):
        self.save_info_button.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_save_info_button_clicked(self):
        # TODO: Add validation
        self.__email = str(self.email_edit.text())
        self.__user_id = str(self.id_edit.text())
        self.__settings.setValue("email", self.__email)
        self.__settings.setValue("id", self.__user_id)

    # helper functions
        
    def __show_notice(self, notice):
        """ Shows message box with notice"""
        mb = QtGui.QMessageBox(self)
        mb.setWindowTitle("Notice.")
        mb.setText(notice)
        mb.setIcon(QtGui.QMessageBox.Information)
        mb.exec_()

    def __show_error(self, error):
        """ Shows message box with error.

        @type error:  str
        @param error: text representation of error"""
        mb = QtGui.QMessageBox(self)
        mb.setWindowTitle("Error!")
        mb.setText(error)
        mb.setIcon(QtGui.QMessageBox.Critical)
        mb.exec_()

class WaitWindow(QtGui.QWidget):

    def __init__(self, enter_window, *args):
        super(WaitWindow, self).__init__(*args)

        self.__enter_window = enter_window

        self.__cancel_button = QtGui.QPushButton(self)
        self.__info_label    = QtGui.QLabel(self)
        self.__cancel_button.setText("Cancel")
        self.__cancel_button.clicked.connect(self.on_cancel)
        self.__info_label.setText("Wait until other players joined the game.")

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.__cancel_button)
        layout.addWidget(self.__info_label)

        self.__enter_window.network.game_started.connect(self.on_game_started)

        self.setLayout(layout)

    # logic
    
    @QtCore.pyqtSlot('PyQt_PyObject')
    def on_game_started(self, data):
        self.__game_window = GameWindow(data, self.__enter_window)
        self.__game_window.show()
        self.close()

    # gui event handlers

    @QtCore.pyqtSlot()
    def on_cancel(self):
        self.__enter_window.show()
        self.close()

class FieldWidget(QtGui.QWidget):
    """ Game field."""

    def __init__(self, init_data, size = (3, 3), cell_size = 32, parent = None):
        super(FieldWidget, self).__init__(parent)

        self.__cell_size = cell_size
        self.__map_height, self.__map_width = size
        self.__generate_field(init_data)
        self.__data = init_data

        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding)

    def set_objects(self, data):
        players = 

    def __set_object_at(self, object, x, y):
        """ Place object `object` at the cell with coords (x, y).

        @type object:  FieldObject
        @param object: Object to place at the sell."""
        if x >= 0 and x < self.__map_width:
            if y >= 0 and y < self.__map_height:
                self.__field[y][x].add_object(object)

    def __del_object_from(self, x, y, object):
        if x >= 0 and x < self.__map_width:
            if y >= 0 and y < self.__map_height:
                self.__field[y][x].del_object(object)

    def __generate_field(self, data):
        cell_size = self.__cell_size
        height, width = self.__map_height, self.__map_width
        self.__field = [[None] * width for x in range(height)]
        for i in xrange(0, height):
            for j in xrange(0, width):
                cell = Cell()
                cell.set_color(QColor(255, 255, 255, 0))
                self.__field[i][j] = cell
        players = data["players"]
        metals  = data["metal"]
        stones  = data["stone"]
        sprite = QImage("observer/images/bot.gif")
        for player in players:
            name = player["name"]
            x, y = player["pos"]
            player_ = Player(sprite, name, 0, 0)
            self.__set_object_at(player_, x, y)
        sprite = QImage("observer/images/wood.jpg")
        for stone in stones:
            x, y = stone
            stone_ = FieldObject(sprite)
            self.__set_object_at(stone_, x, y)
        sprite = QImage("observer/images/brick.jpg")
        for metal in metals:
            x, y = metal
            metal_ = FieldObject(sprite)
            self.__set_object_at(metal_, x, y)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255), 1))
        height, width = self.__map_height, self.__map_width
        for i in xrange(0, height):
            for j in xrange(0, width):
                cell = self.__field[i][j]
                painter.setBrush(QtGui.QBrush(cell.get_color()))
                cell_size = self.__cell_size
                cell_x, cell_y = cell_size * i, cell_size * j 
                painter.drawRect(cell_x, cell_y, cell_size, cell_size)
                objects = cell.get_objects()
                for object in objects:
                    image = object.get_image()
                    x = cell_x + ((cell_size - image.width()) / 2)
                    y = cell_y + ((cell_size - image.height()) / 2)
                    painter.drawImage(x, y, image)

    # Qt service functions

    def minimumSizeHint(self):
        return QtCore.QSize(self.__cell_size * self.__map_height + 2,
                self.__cell_size * self.__map_width + 2)

    def sizeHint(self):
        return QtCore.QSize(self.__cell_size * self.__map_height + 2,
                self.__cell_size * self.__map_width + 2)

form_game_class, base_game_class = uic.loadUiType("observer/game_window.ui")
class GameWindow(QtGui.QWidget, form_game_class):

    __raw_log = ""
    def __init__(self, game_data, enter_window):
        super(GameWindow, self).__init__()

        self.setupUi(self)

        self.game_data = game_data
        h, w = game_data['map_height'], game_data['map_width']
        self.__field = FieldWidget(game_data, (h, w), parent = self)
        
        self.__network = enter_window.network

        self.scroll_area = QtGui.QScrollArea(self)
        self.scroll_area.setWidget(self.__field)
        self.__log = QtGui.QTextDocument()
        self.log_view.setDocument(self.__log)

        self.field_layout.insertWidget(0, self.scroll_area)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Bomberbot")

        self.__network.set_turn_recieving(True)
        self.__network.turn_complete.connect(self.on_turn_complete)
        self.__network.error_occured.connect(self.on_error)

    @QtCore.pyqtSlot('PyQt_PyObject')
    def on_turn_complete(self, data):
        self.__raw_log += "new_turn" + "\n"
        self.__log.setPlainText(self.__raw_log)

    @QtCore.pyqtSlot(str)
    def on_error(self, error):
        print "Error: %s" % str(error)
