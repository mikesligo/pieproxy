''' Copyright 2013 Michael Gallagher

    Email: mikesligo at gmail dot com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. '''

#!/usr/bin/python

import re
import socket               # Import socket module
from threading import Thread
from struct import *

class Packet:
    def __init__(self, packet):
        packet = str(packet)
        print packet
        print "length: "+str(len(packet))
        self.full = packet + "\r\n"
        try:
            host = re.search('\nHost: (\S+)',packet)
            self.host = host.group(1)
        except:
            print "Error finding host"
            print packet
            raise

    def printpacket(self):
        print 'All: \n' + self.full

class Server:
    def __init__(self, host, port):
        self.port = port;
        self.host = host;

    def start(self):
        print "Starting PieProxy..."
        self.mainsocket = socket.socket()
        self.mainsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # don't bind address
        self.mainsocket.bind((host,port))
        self.mainsocket.listen(5)
        print "Starting listen thread..."
        listen = Thread(target=self.listen_for_incoming_client,args=())
        listen.start()
        #self.listen_for_incoming_client()

    def listen_for_incoming_client(self): # To be run in a thread
        while True:
            self.conn, addr = self.mainsocket.accept()     # Establish connection with client.
            packet = self.conn.recv(8192)
            if len(packet) != 0:
                print "\nListening for incoming client..."
                packet = Packet(packet)
                self.forward_packet_to_server(packet)
#               raw_input("\nHit enter to continue")

    def forward_packet_to_server(self, packet):
        print "Forwarding packet to server..."
        s = socket.socket()
        s.settimeout(1.0)
        try:
            if packet is not None: 
                print "Type: "+str(type(packet))
                #print 'Connecting to '+packet.host
            else: 
                print "Host is none"
                print packet.full
            s.connect((packet.host,80))
            s.sendall(packet.full)
            #receive = Thread(target=self.listen_for_incoming_server,args=(s,))
            #receive.start()
            self.listen_for_incoming_server(s)
        except:
            print "\nERROR ATTEMPTING TO CONNECT OR SEND PACKETS"
            print "==========================================="
            print packet.full
            raise

    def listen_for_incoming_server(self,socket):
        print "Listening for incoming packets from the server"
        print "Receiving data..."
        response = socket.recv(8192)
        data = response
        try:
            while len(data) > 0:
                data = socket.recv(8192)
                response = response + data
                print "Receiving more data..."
                print "Length: " + str(len(data))
        finally:
            print "Response Length: " + str(len(response))
            self.return_response_to_client(response)
            socket.close()
            print "Killing thread..."
            return

    def return_response_to_client(self, response):
        print "Returning response to client..."
        self.conn.sendall(response)

    def close(self):
        self.mainsocket.close()

if __name__ == '__main__':
    print
    print "Pie Proxy\n=============================\n"
    host = socket.gethostname() # Get local machine name
    port = 8000                # Reserve port
    server = Server(host,port)
    server.start()
