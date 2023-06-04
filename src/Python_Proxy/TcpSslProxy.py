from . import Proxy, TOCLIENT, TOSERVER, logPackets
import socket
from loguru import logger
from threading import Thread
import ssl

"""
LOOP PARA MAGHINTAY NG CONNECTION
PAG MAY CONNECTION RECV DATA, STORE YUNG SOCKET CONNECTION SA clientServerMap TAPOS GAWA NG CONNECTION PARA SA SERVER LAGAY RIN SA MAP
parehas lang sa tcp, pero, babalutin natin yung server socket natin ng sarili nating certificate, tapos pag magsesend ng data sa tunay na server
isend nang may certificate ng server. 
"""

class TcpSslProxy(Proxy):
    def __init__(self, localIp, localPort, remoteIp, remotePort, hostname, ssl_certfile, ssl_keyfile, bindTo=None, callback=logPackets) -> None:
        self.hostname = hostname
        self.ssl_certfile = ssl_certfile
        self.ssl_keyfile = ssl_keyfile
        super().__init__(localIp, localPort, remoteIp, remotePort, bindTo, callback)


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
                try: #These might be already closed, which will cause an error, just ignore
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
                if(not data): # Empty Data
                    try: #These might be already closed, which will cause an error, just ignore
                        client = [k for k, v in self.clientServerMap.items() if v == SenderSocket][0]
                        SenderSocket.close()
                        client.close()
                        self.RemoveFromMap(client)
                    except Exception as e:
                        pass
            except:
                logger.debug("Connection to Server Closed")
                try: #These might be already closed, which will cause an error, just ignore
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

    def handleClientConnection(self, client_address, connection):
        SenderSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SenderSocket.bind((self.bindTo, 0))
        SenderSocket.connect((self.remoteIp, self.remotePort))
        #SSL SHIT
        context = ssl.create_default_context()
        SenderSocket = context.wrap_socket(SenderSocket, server_hostname=self.hostname)

        #SSL SHIT FOR THE Server Listener
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        logger.debug(self.ssl_keyfile)
        context.load_cert_chain(certfile=self.ssl_certfile, keyfile=self.ssl_keyfile)
        connection = context.wrap_socket(connection, server_side=True)

        self.clientServerMap[connection] = SenderSocket

        #Recv and send THREADS
        ServerListenerThread = Thread(target=self.ServerListener, args=(connection, ))
        ServerListenerThread.start()

        ClientListenerThread = Thread(target=self.ClientListener, args=(SenderSocket, ))
        ClientListenerThread.start()

    def run(self):
        while True:
            connection, client_address  = self.ListenerSocket.accept()
            if connection not in self.clientServerMap:
                logger.success(f"New Client Connection from {client_address[0]}:{client_address[1]}")
                self.handleClientConnection(client_address, connection)