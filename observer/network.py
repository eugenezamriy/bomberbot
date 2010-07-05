# -*- mode:python; coding:utf-8; -*-
# created: 26.06.2010 18:24
# description: Network communictaion
import socket
import json
from time import sleep
from Queue import Queue

from PyQt4 import QtCore
from PyQt4.QtCore import QThread

from observer.errors import NetworkError, WrongPacketError

class Network(QThread):
    """ Separate thread for network communications with server."""

    # private members
    __trailing_part = ""
    __is_connected = False
    __sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    __out_queue = Queue(10)

    # signals
    handshake_complete = QtCore.pyqtSignal('PyQt_PyObject')
    game_started = QtCore.pyqtSignal('PyQt_PyObject')
    turn_complete = QtCore.pyqtSignal('PyQt_PyObject')
    error_occured = QtCore.pyqtSignal(str)

    def __init__(self, host, port):
        super(Network, self).__init__()
        self.__host = host
        self.__port = port

    def run(self):
        """ Main thread loop.

        Main loop wait until appears new message in out queue. If it appears,
        then send it. After sending, execution of thread blocks by recieving
        incoming message from server. When message recieved, broadcasts it 
        to GUI classes using Qt signal/slot mechanism."""
        try:
            self.__connect()
        except NetworkError, e:
            self.error_occured.emit(str(e))
            return

        while True:
            sended = False
            while not sended:
                if self.__out_queue.empty():
                    sleep(0.1) # Avoid cpu eating.
                    continue
                else:
                    message = self.__out_queue.get()
                    self.__send(message)
                    sended = True

            try:
                message = self.__recieve()
            except NetworkError, e:
                self.error_occured.emit(str(e))
            else:
                if message.has_key("status"):
                    if message["status"] == "turn_completed":
                        self.turn_complete.emit(message)
                    elif message["status"] == "game_started":
                        print "game started"
                        self.game_started.emit(message)
                    elif message["status"] == "ok":
                        self.handshake_complete.emit(message)

    def send(self, message):
        self.__out_queue.put(message)

    def disconnect(self):
        if self.__is_connected:
            self.__sock.close()
            self.__is_connected = False
        
    def __connect(self):
        """ Connects to the server host:port"""
        host, port = self.__host, self.__port
        
        if not self.__is_connected:
            try:
                self.__sock.connect((host, port)) 
            except socket.error, e:
                raise NetworkError(e)
            else:
                self.__is_connected = True
        else:
            self.disconnect()
            self.__is_connected = False
            self.__connect()

    def __send(self, packet):
        """ Send packet to the server.
        
        @type packet:  dict
        @param packet: Dict with packet data."""
        try:
            self.__sock.sendall(json.dumps(packet) + "\x00")
        except socket.error, e:
            raise NetworkError(e)

    def __recieve(self):
        """ Recieve incoming data.
        
        @rtype:  dict
        @return: Dict with incoming data."""
        data = ""
        while True:
            if not self.__trailing_part:
                chunk = self.__sock.recv(1024)
                if not chunk:
                    self.__sock.close()
            else:
                chunk = self.__trailing_part
            data += chunk
            nullPos = data.find("\x00")
            if nullPos != -1:
                maybePacket = data[:nullPos]
                self.__trailing_part = data[nullPos + 1:]
                try:
                    packet = json.loads(maybePacket)
                except ValueError:
                    raise WrongPacketError
                else:
                    return packet
