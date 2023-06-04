# Python Proxy
## Multi Purpose UDP, TCP, TCP/SSL Proxy for python

Python Proxy is a proxy library made for python for security minded individuals, or just people wanting to proxy their traffic,
This proxy has implementation for different protocols such as UDP, TCP, and TCP/SSL.

## Installation

Python Proxy can be installed from pip with
`pip install Python_Proxy`

## Usage
To use the library, import it in your python script. 
Udp:
```py
from Python_Proxy import UdpProxy

proxy = UdpProxy('127.0.0.1', 4444, '192.168.18.218', 4444)
proxy.run()
```

TCP:
```py
from Python_Proxy import TcpProxy

proxy = TcpProxy('127.0.0.1', 4444, '192.168.18.218', 4444)
proxy.run()
```

SSL:
For ssl, you have to generate your own certificate files first. This certificate file will be used by the proxy server, and you also have to install the generated certificate as trusted root ca in your computer. For the generation of certificate files, i created a script named `GenerateCertificates.py`. Create the Certificate files `python -m Python_Proxy.GenerateCertificates -H host.com -I 127.0.0.1 -o certs`
```py
from Python_Proxy import TcpSslProxy

proxy = TcpSslProxy('127.0.0.1', 443, '<REMOTE_IP>', 443, 'host.com', '.\certs\server.crt', '.\certs\server.key')
proxy.run()
```

You can also add a custom callback on all the proxies, that allow you to read and modify the data being sent/recieve. Callbacks functions should accept 2 parameters, `data`, which is the data sent/recieved and `toServer` which indiciates where the data is going
```py
from Python_Proxy import UdpProxy

def customCallback(data, toServer):
    if(toServer):
        data = b"MODIFIED"
    return data
    
proxy = UdpProxy('127.0.0.1', 4444, '192.168.18.218', 4444, callback=customCallback)
proxy.run()
```

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://bmc.link/tomorrowisnew1)
