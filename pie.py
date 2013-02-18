#!/usr/bin/python

import re
import socket               # Import socket module
from threading import Thread
from struct import *

class Packet:
    def __init__(self, packet):
        packet = packet[0]
        print packet
        self.full = packet + "\r\n"
        if "GET" in packet[0:3]:
            host = re.search('Host: (\S+)',packet)
            self.host = host.group(1)

    def printpacket(self):
        print 'All: \n' + self.full

class Server:
    def __init__(self, host, port):
        self.port = port;
        self.host = host;
        self.mainsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mainsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # don't bind address
        self.mainsocket.bind((host,port))
        self.mainsocket.listen(5)

    def start(self):
        print "Starting PieProxy..."
        self.conn, addr = self.mainsocket.accept()     # Establish connection with client.
        listen = Thread(target=self.listen_for_incoming_client,args=())
        listen.start()

    def listen_for_incoming_client(self): # To be run in a thread
        while True:
            print "Listening for incoming client..."
            packet = self.conn.recvfrom(8192)
            packet = Packet(packet)
            self.forward_packet_to_server(packet)
            raw_input("\nHit enter to continue")

    def forward_packet_to_server(self, packet):
        print "Forwarding packet to server..."
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print 'Connecting to '+packet.host
            s.connect((packet.host,80))
            s.sendall(packet.full)
        except:
            print "ERROR ATTEMPTING TO CONNET OR SEND PACKETS\n============================\n"
            print packet.full
        self.listen_for_incoming_server(s)

    def listen_for_incoming_server(self,socket):
        print "Listening for incoming packets from the server"
        response = socket.recvfrom(8192)
        response = Packet(response)
        self.return_response_to_client(response)
        socket.close()

    def return_response_to_client(self, response):
        print "Returning response to client..."
        self.conn.sendall(response.full)

    def close(self):
        self.mainsocket.close()

if __name__ == '__main__':
    print
    print "Pie Proxy\n=============================\n"
    host = socket.gethostname() # Get local machine name
    port = 8000                # Reserve port
    server = Server(host,port)
    server.start()
