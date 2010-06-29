# -*- mode:python; coding:utf-8; -*-
# created: 26.06.2010 18:24
# description: Network communictaion
import socket
from threading import Thread
import json

from observer.errors import NetworkError, WrongPacketError

class Network(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__trailing_part = ""
        self.__recievers = []
        self.__is_connected = False

    def run(self):
        while True:
            try:
                message = self.__recieve()
            except NetworkError:
                break
            except WrongPacketError:
                continue
            else:
                if message.has_key("status") and message["status"] == "turn_completed":
                    for i in self.__recievers:
                        i.new_turn(message)
        
    def connect(self, host, port):
        """ Connects to the server host:port"""
        
        if not self.__is_connected:
            try:
                self.__sock.connect((host, port)) 
            except socket.error, e:
                raise NetworkError(e)
            else:
                self.__is_connected = True
        else:
            pass

    def handshake(self, email, id):
        """ Send handshake command to server and gets the answer.
        
        Gets list of registred game types, current games on the server and 
        session_id.

        @type email:   str
        @param email:  email of author of bot

        @rtype:  dict {"session_id": int, "game_types": list of game types, 
                       "games": list of current running games}
        @return: Handshake data returned by server."""
        request = {}
        request["cmd"] = "handshake"
        request["email"] = email
        request["type"] = "player"
        request["id"] = id
        answer = self.__request(request)
        if answer["status"] == "ok":
            data = {"session_id": answer["session_id"]} 
            data["game_types"] = answer["game_types"]
            data["games"] = []
            return answer
        else:
            raise WrongPacketError

    def watch(self, session_id, game_id):
        """ Send watch command to server and gets the answer."""
        request = {}
        request["cmd"] = "watch"
        request["session_id"] = session_id
        request["game_id"] = game_id
        answer = self.__request(request)
        if answer["status"] == "game_running":
            return answer
        else:
            raise WrongPacketError

    def add_reciever(self, reciever):
        if reciever not in self.__recievers:
            self.__recievers.append(reciever)

    def remove_reciever(self, reciever):
        if reciever in self.__recievers:
            self.__recievers.remove(reciever)
        

    def __request(self, packet):
        """ Made request to the server and gets the answer.
        
        @type packet: dict
        @param packet: Dict with packet data.

        @return: packet with server answer (in form of dict)"""
        # All the exception handling lies on high levels
        self.__send(packet)
        answer = self.__recieve()
        return answer

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

    def close(self):
        if self.__is_connected:
            self.__sock.close()
            self.__is_connected = False
