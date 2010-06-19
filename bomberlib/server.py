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
        while True:                        
            readables, writeables, exceptions = select(self.readsocks, self.writesocks, [])
            for sockobj in readables:
                if sockobj in self.mainsocks:                 
                    newsock, address = sockobj.accept()
                    print 'Client connected:', address, id(newsock)
                    self.readsocks.append(newsock)
                else:
                    data = sockobj.recv(1024)
                    if not data:
                        sockobj.close()
                        self.readsocks.remove(sockobj)
                    try:
                        data = json.loads(data)
                    except EOFError:
                        sockobj.close()
                        if sockobj in self.readsocks:
                            self.readsocks.remove(sockobj)
                        continue
                    
                    self.Q.append((datetime.datetime.now(), data))

            while True:
                if (len(writeables) == 0) or (len(self.Q) == 0):
                    break
                message = self.Q[0]

                for sockobj in writeables:
                    try:
                        sockobj.send(pickle.dumps(message[1]))
                    except:
                        pass
                self.Q.remove(message)
        time.sleep(0.1)
        return

    def handleQuit(self):
        for sock in self.mainsocks:
            sock.close()
        for sock in self.readsocks:
            sock.close()
        for sock in self.writesocks:
            sock.close()
        return
                
if __name__=="__main__":
    BomberBot = Server("",41000)
    try:
        BomberBot.Serve()
    finally:
        for sock in BomberBot.mainsocks:
            sock.close()
