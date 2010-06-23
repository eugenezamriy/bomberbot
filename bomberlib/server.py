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
        
        mainsocks, readsocks = [], []

        portsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        portsock.bind((self.bind_address, self.bind_port))
        portsock.listen(5)
        mainsocks.append(portsock)
        readsocks.append(portsock)
            
        self.mainsocks = mainsocks
        self.readsocks = readsocks
        self.writesocks = []
      
    def serve(self):
        data = {}
        while True:
            try:
                readables, writeables, exceptions = select(self.readsocks, self.writesocks, [])
            except socket.error, e:
                # seems one of our sockets broken - find it
                # TODO: this is really ugly code and must be rewrited
                for sockobj in set(self.readsocks + self.writesocks):
                    try:
                        _, _, _ = select([sockobj], [sockobj], [], 0)
                    except socket.error, e:
                        if sockobj in self.readsocks:
                            self.readsocks.remove(sockobj)
                        if sockobj in self.writesocks:
                            self.writesocks.remove(sockobj)
                        # clean data dictionary to avoid memory leaks
                        if sockobj in data:
                            del(data[sockobj])
                continue
            for sockobj in readables:
                if sockobj in self.mainsocks:                 
                    newsock, address = sockobj.accept()
                    debug("client connected: %s, %s" % (address, id(newsock)))
                    self.readsocks.append(newsock)
                    # NOTE: moved to message receiving block but dunno what is better
                    #self.writesocks.append(newsock)
                else:
                    s_id = id(sockobj)            # socket id
                    chunk = sockobj.recv(1024)
                    if not chunk:
                        sockobj.close()
                        self.readsocks.remove(sockobj)
                        continue

                    try:
                        data[sockobj] += chunk
                    except KeyError:
                        data[sockobj] = chunk
                        
                    nullPos = data[sockobj].find("\x00")
                    while nullPos != -1:
                        maybeMessage = data[sockobj][:nullPos]
                        data[sockobj] = data[sockobj][nullPos + 1:]
                        nullPos = data[sockobj].find("\x00")
                        try:
                            message = json.loads(maybeMessage)
                        except ValueError, e:
                            error("can't decode message from %s (%s): %s" % \
                                  (s_id, str(e), maybeMessage))
                            # if json isn't valid sends to the client 
                            # status:error packet
                            # TODO: do more general error-report system
                            self.out_queue.put((s_id, json.dumps('{"status":"error"}')))
                            if sockobj not in self.writesocks:
                                self.writesocks.append(sockobj)
                        except EOFError:
                            sockobj.close()
                            if sockobj in self.readsocks:
                                self.readsocks.remove(sockobj)
                            continue
                        else:
                            # seems message was received successfully, put it to processing queue
                            debug("received message from %s: %s" % (s_id, message))
                            self.in_queue.put((datetime.datetime.now(), s_id, message),
                                              block=True)
                            if sockobj not in self.writesocks:
                                self.writesocks.append(sockobj)
                            # NOTE: with this lines server acts as echo server. must be removed
                            #       later (when messages dispatcher 'll be done).
                            (_, _, _) = self.in_queue.get(block=True)
                            self.out_queue.put((s_id, message))

            while True:
                if (len(writeables) == 0) or self.out_queue.empty():
                    break
                try:
                    s_id, message = self.out_queue.get(block=False)
                except Queue.Empty:
                    break
                # TODO: send message only to socket with s_id
                for sockobj in writeables:
                    try:
                        sockobj.send(json.dumps(message) + "\x00")
                    except:
                        pass
            
            time.sleep(0.1)

    def handleQuit(self):
        for sock in self.mainsocks:
            sock.close()
        for sock in self.readsocks:
            sock.close()
        for sock in self.writesocks:
            sock.close()
