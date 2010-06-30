# -*- mode:python; coding:utf-8; -*-
# created: 27.06.2010 12:19
# description: GUI part of observer

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt, QSettings

from observer.network import Network
from observer.logic import Player, Cell
from observer.errors import NetworkError
from observer.misc import TableModel

form_class, base_class = uic.loadUiType("observer/enter_window.ui")

class EnterWindow(QtGui.QWidget, form_class):

    def __init__(self, network, *args):
        super(EnterWindow, self).__init__(*args)
        self.setupUi(self)

        self.__games = []
        self.__game_types = [] 
        self.__selected_row = []
        self.__network = network 
        self.__settings = QSettings(self)
        self.__server = str(self.__settings.value("server", "localhost:41000").toString())
        self.__email = str(self.__settings.value("email", "test@example.com").toString())
        self.__id = str(self.__settings.value("id", "test_id1").toString())

        self.id_edit.setText(self.__id)
        self.email_edit.setText(self.__email)
        self.server_edit.setText(self.__server)
        self.save_info_button.setEnabled(False)
        self.setWindowTitle("Observer")
        self.setLayout(self.main_layout)

    @QtCore.pyqtSlot()
    def on_email_edit_textChanged(self):
        self.save_info_button.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_id_edit_textChanged(self):
        self.save_info_button.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_save_info_button_clicked(self):
        """ Called every time when user clicks save_info_button."""
        # TODO: Add validation
        self.__email = self.email_edit.text()
        self.__id = self.id_edit.text()
        self.__settings.setValue("email", self.__email)
        self.__settings.setValue("id", self.__id)

    @QtCore.pyqtSlot()
    def on_connect_button_clicked(self):
        """ Called every time when user clicks connect_button."""
        port = 0
        host = ""
        # Get server address from input field.
        server_address = str(self.server_edit.text())
        # Validate server_address string and divides it into host and port
        # TODO: Add more validation.
        delim_pos = server_address.find(":")
        if delim_pos != -1:
            host = server_address[:delim_pos]
            port = int(server_address[delim_pos + 1:])
        if delim_pos == -1 or host == "" or port == 0:
            self.__show_error("Wrong server address. Please enter a right one.")
            return 
        # Connect to server.
        try:
            self.__network.connect(host, port)
        except NetworkError, e:
            self.__show_error(str(e))
        else:
            try:
                # Do handshake request and recieve server answer.
                data = self.__network.handshake(self.__email, self.__id)
            except NetworkError, e:
                self.__show_error(str(e))
            else:
                self.__game_types = data["game_types"]
                # TODO: replace with proper data.
                self.games = []
                # Put all recieved information in `games_table`.
                self.__set_table_data()

    @QtCore.pyqtSlot()
    def on_join_button_clicked(self):
        """ Called every time when user clicks join_button."""
        current_row = self.sel_model.selectedRows()[0].row()
        game = self.__game_types[current_row]
        self.game_window = GameWindow(game, self.__network)
        self.game_window.show()
        self.hide()

    @QtCore.pyqtSlot()
    def on_games_table_selection_changed(self):
        """ Called every time when user changes selection in games_table."""
        self.join_button.setEnabled(True)

    def __set_table_data(self):
        """ Puts data from self.__game_types to self.games_table."""
        if len(self.__game_types) > 0:
            headers = ["Game Type", "Init Bombs Count", "Max Players Count",
                "field_size"]
            # Prepare data to inserting in `games_table`.
            data = [[x["type_id"], x["init_bombs_count"], x["max_players_count"],
                     str(x["map_height"]) + "x" + str(x["map_width"])] 
                     for x in self.__game_types]
            self.games_table.setModel(TableModel(data, headers, self))
            self.games_table.resizeColumnsToContents()
            # Set selection changes handler
            self.sel_model = self.games_table.selectionModel()
            self.sel_model.selectionChanged.connect(self.on_games_table_selection_changed)
        else:
            self.__show_notice("No started games found. Try again later.")
        
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


class FieldWidget(QtGui.QWidget):
    """ Game field."""

    def __init__(self, size = (3, 3), cell_size = 30, parent = None):
        super(FieldWidget, self).__init__(parent)

        self.cell_size = cell_size
        self.cell_vertical, self.cell_horizontal = size
        self.cells = self.__generate_field()

        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Expanding)

    def minimumSizeHint(self):
        return QtCore.QSize(self.cell_size * self.cell_vertical + 2,
                self.cell_size * self.cell_horizontal + 2)

    def sizeHint(self):
        return QtCore.QSize(self.cell_size * self.cell_vertical + 2,
                self.cell_size * self.cell_horizontal + 2)

    def set_object_at(self, x, y, object):
        """ Sets object `object` at the cell with coords (x, y).
        
        @type x:       int
        @param x:      x coordinate.
        @type y:       int
        @param y:      y coordinate.
        @type object:  FieldObject
        @param object: Object to set at the sell."""
        self.cells[x][y].set_object(object)

    def __generate_field(self):
        cell_size = self.cell_size
        vsize, hsize = self.cell_vertical, self.cell_horizontal
        field = [[None] * hsize for x in range(vsize)]
        for i in xrange(0, vsize):
            for j in xrange(0, hsize):
                cell = Cell(cell_size)
                cell.set_pos((i * cell_size, j * cell_size))
                field[i][j] = cell
        return field

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255), 1))
        for cells_row in self.cells:
            for cell in cells_row:
                painter.setBrush(QtGui.QBrush(cell.get_color()))
                cell_x, cell_y = cell.get_pos()
                cell_size = cell.get_size()
                painter.drawRect(cell_x, cell_y, cell_size, cell_size)
                object = cell.get_object()
                if object:
                    image = object.get_image()
                    x = cell_x + ((cell_size - image.width()) / 2)
                    y = cell_y + ((cell_size - image.height()) / 2)
                    painter.drawImage(x, y, image)


form_game_class, base_game_class = uic.loadUiType("observer/game_window.ui")
class GameWindow(QtGui.QWidget, form_game_class):

    def __init__(self, game_data, network):
        super(GameWindow, self).__init__()

        self.setupUi(self)

        self.game_data = game_data
        h, w = game_data['map_height'], game_data['map_width']
        self.field = FieldWidget((h, w), parent = self)
        
        self.network = network
        self.network.add_reciever(self.new_turn)

        self.scroll_area = QtGui.QScrollArea(self)
        self.scroll_area.setWidget(self.field)

        player = Player("imgages/bot.gif", (0, 0))
        self.field.set_object_at(0, 0, player)

        self.field_layout.insertWidget(0, self.scroll_area)

        self.setLayout(self.main_layout)
        self.setWindowTitle("Bomberbot")

    def new_turn(self, data):
        pass
