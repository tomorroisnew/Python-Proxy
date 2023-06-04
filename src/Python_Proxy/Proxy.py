import socket
import threading

def logPackets(data, toServer):
    if(toServer):
        print("[client] {}".format(str(data)))
    else:
        print("[server] {}".format(str(data)))
    return data

class Proxy(threading.Thread):
    def __init__(self, localIp, localPort, remoteIp, remotePort, useLocalIp, callback=logPackets) -> None:
        threading.Thread.__init__(self)
        self.localIp = localIp
        self.localPort = localPort
        self.remoteIp = remoteIp
        self.remotePort = remotePort
        self.useLocalIp = useLocalIp
        self.callback = callback

    def run(self):
        raise NotImplementedError
    
    def getLocalIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]