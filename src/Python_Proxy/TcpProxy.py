from . import Proxy, TOCLIENT, TOSERVER
import socket
from loguru import logger
from threading import Thread

"""
LOOP PARA MAGHINTAY NG CONNECTION
PAG MAY CONNECTION RECV DATA, STORE YUNG SOCKET CONNECTION SA clientServerMap TAPOS GAWA NG CONNECTION PARA SA SERVER LAGAY RIN SA MAP

"""

class TcpProxy(Proxy):
    def init(self):
        self.ListenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ListenerSocket.bind((self.localIp, self.localPort))
        self.ListenerSocket.listen()
        logger.debug(f"Listening on {self.localIp}:{self.localPort}")

        self.clientServerMap = {}

    def RemoveFromMap(self, Key = None, Value = None):
        if(Key):
            self.clientServerMap.pop(Key)
        elif(Value):
            key = [k for k, v in self.clientServerMap.items() if v == Value][0]
            self.clientServerMap.pop(Key)
            
    def ExistsInMap(self, Key = None, Value = None):
        if(Key):
            if Key in self.clientServerMap:
                return True
            else:
                return False
        elif(Value):
            if Value in self.clientServerMap.values():
                return True
            else:
                return False

    def ServerListener(self, connection: socket.socket): # Serve as server. Listens from the game client
        while True and self.ExistsInMap(connection):
            try:
                data = connection.recv(4026)
            except Exception as e:
                logger.debug("Connection to Client Closed")
                try: #These might be already closed
                    connection.close()
                    self.clientServerMap[connection].close()
                    self.RemoveFromMap(None, connection)
                except:
                    pass
                return
            
            data = self.callback(data, TOSERVER)

            self.clientServerMap[connection].sendall(data)

    def ClientListener(self, SenderSocket: socket.socket): # Serve as the client. Listens for data coming from the real server
        while True and self.ExistsInMap(None, SenderSocket):
            try:
                data = SenderSocket.recv(4026)
            except:
                logger.debug("Connection to Server Closed")
                try: #These might be already closed
                    client = [k for k, v in self.clientServerMap.items() if v == SenderSocket][0]
                    SenderSocket.close()
                    client.close()
                    self.RemoveFromMap(client)
                except Exception as e:
                    pass
                return
            client = [k for k, v in self.clientServerMap.items() if v == SenderSocket][0] # Is there an easier way to do this
            data = self.callback(data, TOCLIENT)
            client.sendall(data)

    def handleClientConnection(self, client_address, conneciton):
        SenderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SenderSocket.bind((self.bindTo, 0))
        SenderSocket.connect((self.remoteIp, self.remotePort))

        self.clientServerMap[conneciton] = SenderSocket

        #Recv and send THREADS
        ServerListenerThread = Thread(target=self.ServerListener, args=(conneciton, ))
        ServerListenerThread.start()

        ClientListenerThread = Thread(target=self.ClientListener, args=(SenderSocket, ))
        ClientListenerThread.start()

    def run(self):
        while True:
            connection, client_address  = self.ListenerSocket.accept()
            if connection not in self.clientServerMap:
                logger.success(f"New Client Connection from {client_address[0]}:{client_address[1]}")
                self.handleClientConnection(client_address, connection)