#!/usr/bin/python

import re
import socket               # Import socket module
from struct import *

class Packet:
    def __init__(self, packet):
        packet = packet[0]
        print packet
        self.full = packet + "\r\n"
        if "GET" in packet[0:3]:
            host = re.search('Host: (\w+).(\w+).(\w+)',packet)
            host = host.group(1) +'.'+ host.group(2) +'.'+ host.group(3)
            if host is None:
                host = re.search('Host: (\w+).(\w+)',packet)
                host = host.group(1) +'.'+ host.group(2)
            self.host = host

    def printpacket(self):
        print 'All: \n' + self.full

class Server:
    def __init__(self, host, port):
        self.port = port;
        self.host = host;
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # don't bind address
        self.s.bind((host,port))
        self.s.listen(5)

    def receive(self):
        conn, addr = self.s.accept()     # Establish connection with client.

        packet = conn.recvfrom(8192)
        packet = Packet(packet)
        response = self.forward_packet(packet)
        conn.sendall(response.full)

        conn.close()

    def forward_packet(self, packet):
        s = socket.socket()
        print 'Connecting to '+packet.host
        s.connect((packet.host,80))
        s.sendall(packet.full)
        response = s.recvfrom(8192)
        response = Packet(response)
        s.close()
        return response

    def send_socket(self,socket):
        socket.send('Thank you for connecting')

    def close(self):
        self.s.close()

if __name__ == '__main__':
    print "Pie Proxy\n=============================\n"
    host = socket.gethostname() # Get local machine name
    port = 8000                # Reserve port
    server = Server(host,port)
    server.receive()
