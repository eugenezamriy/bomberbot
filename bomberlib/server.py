# -*- mode:python; coding:utf-8; -*-
# created: 19.06.2010 16:21 UTC
# description: BomberBot server.


import datetime
import json
from select import select
from socket import socket, AF_INET, SOCK_STREAM
import time


class Server:

    def __init__(self, HOSTNAME, PORT):
        self.HOSTNAME = HOSTNAME
        self.PORT = PORT
        
        mainsocks, readsocks = [], []

        portsock = socket(AF_INET, SOCK_STREAM)
        portsock.bind((HOSTNAME, PORT))
        portsock.listen(5)
        mainsocks.append(portsock)
        readsocks.append(portsock)
            
        self.mainsocks = mainsocks
        self.readsocks = readsocks
        self.writesocks = []

        self.Q = []
      
    def serve(self):
        data = {}
        while True:                        
            readables, writeables, exceptions = select(self.readsocks, self.writesocks, [])
            for sockobj in readables:
                if sockobj in self.mainsocks:                 
                    newsock, address = sockobj.accept()
                    print 'Client connected:', address, id(newsock)
                    self.readsocks.append(newsock)
                else:                    
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
                        except ValueError:
                            pass
                        except EOFError:
                            sockobj.close()
                            if sockobj in self.readsocks:
                                self.readsocks.remove(sockobj)
                            continue
                        else:
                            self.Q.append((datetime.datetime.now(), id(sockobj), message))

            while True:
                if (len(writeables) == 0) or (len(self.Q) == 0):
                    break
                message = self.Q[0]

                for sockobj in writeables:
                    try:
                        sockobj.send(json.dumps(message[1]))
                    except:
                        pass
                self.Q.remove(message)
            
            time.sleep(0.1)

    def handleQuit(self):
        for sock in self.mainsocks:
            sock.close()
        for sock in self.readsocks:
            sock.close()
        for sock in self.writesocks:
            sock.close()
