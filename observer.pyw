# -*- mode:python; coding:utf-8; -*-
# created: 26.06.2010 22:58
# description: Main observer file
import sys

from PyQt4 import QtCore, QtGui

from observer.gui import EnterWindow
from observer.network import Network

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    network = Network()
    window = EnterWindow(network)
    window.show()
    sys.exit(app.exec_())
