# -*- mode:python; coding:utf-8; -*-
# created: 24.06.2010 15:52 UTC
# description: Client for testing BomberBot server.
import socket, sys, struct

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
    if len(sys.argv) != 4:
        print "Usage: %s host port message" % sys.argv[0]
    else:
        host, port, message = sys.argv[1:]
        port = int(port)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            print "Request: ", message
            send(sock, message)
            sock.close()
        except Exception, err:
            print "Error: %s\n" % str(err)
