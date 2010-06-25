# -*- mode:python; coding:utf-8; -*-
# created: 19.06.2010 16:21 UTC
# description: BomberBot server.


import datetime
import json
from select import select
import socket
#from socket import socket, AF_INET, SOCK_STREAM
import time
import Queue

from bomberlib.logger import debug, error


class Server:

    def __init__(self, address, port, in_queue, out_queue):
        """
        @type address:    str
        @param address:   IP address to bind server on.
        @type port:       int
        @param port:      Port to listen on.
        @type in_queue:   Queue.Queue
        @param in_queue:  Incoming messages queue (timestamp, socket id, message).
        @type out_queue:  Queue.Queue
        @param out_queue: Outgoing messages queue (socket id, message).
        """
        self.bind_address = address
        self.bind_port = port
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.data = {}                            # incompleted messages buffer
        self.main_socks, self.read_socks, self.write_socks = [], [], []
        port_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_sock.bind((self.bind_address, self.bind_port))
        port_sock.listen(5)
        self.main_socks.append(port_sock)
        self.read_socks.append(port_sock)
      
    def serve(self):
        while True:
            try:
                readables, writeables, exceptions = select(self.read_socks, self.write_socks, [])
            except socket.error, e:
                # seems one of our sockets broken - find it
                for sockobj in set(self.read_socks + self.write_socks):
                    try:
                        _, _, _ = select([sockobj], [sockobj], [], 0)
                    except socket.error, e:
                        self.__remove_socket(sockobj)
                continue
            # read incoming messages
            for sockobj in readables:
                if sockobj in self.main_socks:                 
                    newsock, address = sockobj.accept()
                    debug("client connected: %s, %s" % (address, id(newsock)))
                    self.read_socks.append(newsock)
                    self.write_socks.append(newsock)
                else:
                    s_id = id(sockobj)            # socket id
                    chunk = sockobj.recv(1024)
                    if not chunk:
                        self.__remove_socket(sockobj)
                        continue
                    #
                    if self.data.has_key(s_id):
                        self.data[s_id] += chunk
                    else:
                        self.data[s_id] = chunk
                    #
                    nullPos = self.data[s_id].find("\x00")
                    while nullPos != -1:
                        maybe_message = self.data[s_id][:nullPos]
                        self.data[s_id] = self.data[s_id][nullPos + 1:]
                        nullPos = self.data[s_id].find("\x00")
                        try:
                            message = json.loads(maybe_message)
                        except ValueError, e:
                            error("can't decode message from %s (%s): %s" % \
                                  (s_id, str(e), maybe_message))
                            self.out_queue.put((s_id, {"status": "error", "reason": str(e)}))
                        else:
                            # seems message was received successfully, put it to processing queue
                            debug("received message from %s: %s" % (s_id, message))
                            self.in_queue.put((datetime.datetime.now(), s_id, message),
                                              block=True)
                            # NOTE: with this lines server acts as echo server. must be removed
                            #       later (when messages dispatcher 'll be done).
                            (_, _, _) = self.in_queue.get(block=True)
                            self.out_queue.put((s_id, message))
            # send outgoing messages
            while True:
                if len(writeables) == 0 or self.out_queue.empty():
                    break
                try:
                    s_id, message = self.out_queue.get(block=True)
                except Queue.Empty:
                    break
                for sockobj in writeables:
                    if id(sockobj) == s_id:
                        try:
                            debug("sending message to %s: %s" % (s_id, json.dumps(message)))
                            sockobj.sendall(json.dumps(message) + "\x00")
                        except:
                            pass
                        break
            time.sleep(0.1)                       # make some delay to avoid CPU eating

    def __remove_socket(self, sockobj):
        sockobj.close()
        if sockobj in self.read_socks:
            self.read_socks.remove(sockobj)
        if sockobj in self.write_socks:
            self.write_socks.remove(sockobj)
        id_ = id(sockobj)
        if self.data.has_key(id_):
            del(self.data[id_])

    def handleQuit(self):
        for sock in self.mainsocks:
            sock.close()
        for sock in self.readsocks:
            sock.close()
        for sock in self.writesocks:
            sock.close()
