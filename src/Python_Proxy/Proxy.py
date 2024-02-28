import socket
import threading
from loguru import logger

TOCLIENT = 0
TOSERVER = 1

def logPackets(data, toServer):
    if(toServer):
        print("[client] {}".format(str(data)))
    else:
        print("[server] {}".format(str(data)))
    return data

class Proxy(threading.Thread):
    def __init__(self, localIp, localPort, remoteIp=None, remotePort=None, remoteHost=None, bindTo=None, callback=logPackets) -> None:
        threading.Thread.__init__(self)
        self.localIp = localIp
        self.localPort = localPort
        self.remoteIp = remoteIp
        self.remotePort = remotePort
        self.remoteHost = remoteHost
        if bindTo == None: # Use default ip
            self.bindTo = self.getLocalIp()
            logger.debug(self.bindTo)
        else:
            self.bindTo = bindTo
        self.callback = callback

        self.init()

    def init(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
    
    def getLocalIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]