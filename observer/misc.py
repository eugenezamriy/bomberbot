# -*- mode:python; coding:utf-8; -*-
# created: 29.06.2010 14:53
# description: 

from PyQt4 import QtCore
from PyQt4.QtCore import Qt

class TableModel(QtCore.QAbstractTableModel):
    """ Model for QTableView widgets."""

    def __init__(self, data, headers, parent = None, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.data = data
        self.headers = headers

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role != Qt.DisplayRole: 
            return QtCore.QVariant()
        return QtCore.QVariant(self.data[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return QtCore.QVariant(self.headers[col])
