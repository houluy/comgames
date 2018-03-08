import socket
import socketserver

class Client:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, data):
        self.socket.send(data.encode())

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(100)
        print(self.data)

class Server(socketserver.ThreadingTCPServer):
    def __init__(self, host, port):
        super().__init__((host, port), TCPHandler)

