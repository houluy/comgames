import socket

class Client:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, data):
        self.socket.send(data.encode())

