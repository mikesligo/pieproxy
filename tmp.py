import socket
s = socket.socket()
s.bind(('127.0.0.1', 8000))
c, addr = s.accept()
while True:
    print c.recvfrom(65535)
