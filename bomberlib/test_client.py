# -*- mode:python; coding:utf-8; -*-
# created: 24.06.2010 15:52 UTC
# description: Client for testing BomberBot server.
import socket, sys, struct, json

def send(socket, message):
    """ Sends a message with null-terminator."""
    totalsent = 0
    while totalsent < len(message):
        sent = socket.send(message[totalsent:])
        if sent == 0:
            raise RuntimeError, "Socket connection broken"
        totalsent += sent
    socket.send("\x00")

if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        print "Usage: %s host port message count(optional)" % sys.argv[0]
    else:
        host, port, message = sys.argv[1:4]
        port = int(port)
        count = int(sys.argv[4]) if len(sys.argv) == 5 else 1
        if message == "handshake":
            message = json.dumps({"cmd": "handshake", "type": "player", "id": "test_id1", "email": "test@example.com"})
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            print "Request: ", message
            for i in range(count):
                send(sock, message)
                print "Request sended"
                print sock.recv(1024)
            sock.close()
        except Exception, err:
            print "Error: %s\n" % str(err)
