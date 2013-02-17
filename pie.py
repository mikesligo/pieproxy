#!/usr/bin/python

import socket               # Import socket module
from struct import *

class Packet:
    ''' 
    Custom packet class.
    Attributes created on initialisation:

    IP
    ============
    - version
    - ihl
    - ttl
    - protocol
    - s_addr
    - d_addr
    
    TCP
    ============
    - source port
    - dest_port
    - sequence
    - acknowledgement
    - tcph_length

    - data
    '''

    def __init__(self, packet):
        packet = packet[0]
        self.full = packet
        if "GET" not in packet[0:3]:
            print "EXPECTING GET REQUEST"
            print packet

        #parse ethernet header
        eth_length = 14
        
        eth_header = packet[:eth_length]
        eth = unpack('!6s6sH' , eth_header)

        self.eth_protocol = socket.ntohs(eth[2])
        self.dest_mac = packet[0:6]
        self.src_mac = packet[6:12]

            
        # get tcp/ip data
        ip_header = packet[0:20]
        iph = unpack('!BBHHHBBH4s4s' , ip_header) # Unpack ip header with formatting

        version_ihl = iph[0]
        self.version = version_ihl >> 4
        self.ihl = version_ihl & 0xF
        iph_length = self.ihl * 4
        self.ttl = iph[5]
        self.protocol = iph[6]
        self.s_addr = socket.inet_ntoa(iph[8]);
        self.d_addr = socket.inet_ntoa(iph[9]);

        tcp_header = packet[iph_length:iph_length+20]
        tcph = unpack('!HHLLBBHHH' , tcp_header) # Unpack tcp header with formatting

        self.source_port = tcph[0]
        self.dest_port = tcph[1]
        self.sequence = tcph[2]
        self.acknowledgement = tcph[3]
        doff_reserved = tcph[4]
        self.tcph_length = doff_reserved >> 4
        
        h_size = (eth_length + iph_length + self.tcph_length) * 4
        print "H_SIZE " + str(h_size/4)
        self.data = packet[0:]

    def printpacket(self):
        print 'Version : ' + str(self.version) + ' IP Header Length : ' + str(self.ihl) + ' TTL : ' + str(self.ttl) + ' Protocol : ' + str(self.protocol) + ' Source Address : ' + str(self.s_addr) + ' Destination Address : ' + str(self.d_addr)
        print 'Source Port : ' + str(self.source_port) + ' Dest Port : ' + str(self.dest_port) + ' Sequence Number : ' + str(self.sequence) + ' Acknowledgement : ' + str(self.acknowledgement) + ' TCP header length : ' + str(self.tcph_length) 
        print 'Data: ' + self.data

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
        print packet[0]
        packet = Packet(packet)
        packet.printpacket()
        conn.close()
        self.forward_packet(packet)

    def forward_packet(self, packet):
        s = socket.socket()
        s.connect((packet.d_addr,80))
        s.sendall(packet.data)
        print s.recvfrom(8192)

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
    server.receive()
