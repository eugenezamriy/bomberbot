"""
BomberBot Server
"""

import sys
import datetime
import thread
import json
from select import select
from socket import socket, AF_INET, SOCK_STREAM

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
        data = ""
        while True:                        
            readables, writeables, exceptions = select(self.readsocks, self.writesocks, [])
            trailingData = {}
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
                        trailingData[sockobj] += chunk
                    except KeyError:
                        trailingData[sockObj] = chunk
                        
                    nullPos = trailingData[sockObj].find("\x00")
                    while nullPos != -1:
                        maybeMessage = data[:nullPos]
                        trailingData[sockObj] = trailingData[sockObj][nullPos + 1:]
                    
                        try:
                            message = json.loads(maybeMessage)
                        except EOFError:
                            sockobj.close()
                            if sockobj in self.readsocks:
                                self.readsocks.remove(sockobj)
                            continue
                    
                        self.Q.append((datetime.datetime.now(), id(sockobj), message))
                        nullPos = trailingData[sockObj].find("\x00")

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
                
if __name__=="__main__":
    BomberBot = Server("",41000)
    try:
        BomberBot.serve()
    finally:
        for sock in BomberBot.mainsocks:
            sock.close()
