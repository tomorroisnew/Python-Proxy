from . import Proxy

import requests
from http.server import (
    BaseHTTPRequestHandler,
    HTTPServer
)
from socketserver import ThreadingMixIn

from loguru import logger


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET(body=False)
        return

    def do_GET(self, body=True):
        sent = False
        try:
            url = '{}{}'.format(self.remoteHost, self.path)
            req_header = self.parse_headers()

            logger.debug(req_header)
            logger.debug(url)
            resp = requests.get(url, headers=req_header, verify=self.verify)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            msg = resp.text
            if body:
                self.wfile.write(msg.encode(encoding='UTF-8', errors='strict'))
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def do_POST(self, body=True):
        sent = False
        try:
            url = '{}{}'.format(self.remoteHost, self.path)
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            req_header = self.parse_headers()
            logger.debug(req_header)
            logger.debug(url)
            logger.debug(post_body)
            resp = requests.post(url, data=post_body, headers=req_header, verify=self.verify)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def parse_headers(self):
        req_header = {}
        for line in self.headers:
            line_parts = [o.strip() for o in line.split(':', 1)]
            if len(line_parts) == 2:
                req_header[line_parts[0]] = line_parts[1]
        return req_header

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        logger.debug('Response Headers:')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                logger.debug(key + ': ' + respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(resp.content))
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class HttpReverseProxy(Proxy):
    def init(self):
        class HttpHandler(ProxyHTTPRequestHandler):
            remoteHost = self.remoteHost if self.remoteHost else f'http://{self.remoteIp}:{self.remotePort}'
            remoteHost = remoteHost if (remoteHost.startswith('http://') or remoteHost.startswith('https://')) else f'http://{remoteHost}'
            verify = True
            protocol_version = 'HTTP/1.1'

            def merge_two_dicts(self, x, y):
                return x | y

            def set_header(self):
                return {'Host': self.remoteHost}

        self.handler = HttpHandler
        return self

    def run(self):
        with ThreadedHTTPServer((self.localIp, self.localPort), self.handler) as httpd:
            logger.info(f"Listening on {self.localIp}:{self.localPort}")
            httpd.serve_forever()
