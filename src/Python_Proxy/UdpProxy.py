from Python_Proxy.Proxy import logPackets
from . import Proxy, TOCLIENT, TOSERVER
import socket
from loguru import logger
from threading import Thread

class UdpProxy(Proxy):
    def init(self):
        self.ListenerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.ListenerSocket.bind((self.localIp, self.localPort))

        self.clientServerMap = {}

    def recv_from(self, client_address):
        while True:
            data, _ = self.clientServerMap[client_address].recvfrom(65534)
            data = self.callback(data, TOCLIENT)
            self.ListenerSocket.sendto(data, client_address)

    def handleClientConnection(self, client_address, initial_data):
        SenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        SenderSocket.bind((self.bindTo, 0))

        self.clientServerMap[client_address] = SenderSocket
        recieve_thread = Thread(target=self.recv_from, args=(client_address, ))
        recieve_thread.start()

    def run(self):
        while True:
            data, client_address = self.ListenerSocket.recvfrom(65534)
            if client_address not in self.clientServerMap:
                logger.success(f"New Client Connection from {client_address[0]}:{client_address[1]}")
                self.handleClientConnection(client_address, data)
            data = self.callback(data, TOSERVER)
            self.clientServerMap[client_address].sendto(data, (self.remoteIp, self.remotePort))