from . import logPackets
from . import Proxy
import socket
from loguru import logger
from threading import Thread

class UdpProxy(Proxy):
    def __init__(self, localIp, localPort, remoteIp, remotePort, useLocalIp, callback=...) -> None:
        super().__init__(localIp, localPort, remoteIp, remotePort, useLocalIp, callback)

        self.ListenerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.ListenerSocket.bind((self.localIp, self.localPort))

        self.clientServerMap = {}

    def recv_from(self, client_address):
        while True:
            data, _ = self.clientServerMap[client_address].recvfrom(65534)
            self.ListenerSocket.sendto(data, client_address)

    def handleClientConnection(self, client_address, initial_data):
        SenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.useLocalIp:
            SenderSocket.bind((self.getLocalIp(), 0))

        self.clientServerMap[client_address] = SenderSocket
        recieve_thread = Thread(target=self.recv_from, args=(client_address, ))
        recieve_thread.start()

    def run(self):
        while True:
            data, client_address = self.ListenerSocket.recvfrom(65534)
            if client_address not in self.clientServerMap:
                logger.success(f"New Client Connection from {client_address[0]}:{client_address[1]}")
                self.handleClientConnection(client_address, data)
            self.clientServerMap[client_address].sendto(data, (self.remoteIp, self.remotePort))