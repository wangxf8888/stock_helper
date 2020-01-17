#!/usr/bin/python
# -*- coding: utf-8 -*-

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import argparse
import re
import modules.user
import signal
import sys
import time

g_close = False


def sigint_handler(signal, frame):
    global g_close
    g_close = True


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.search(r'/user/register/*', self.path) is not None:
            req_strs = self.path.split('/')
            if len(req_strs) >= 2:
                user_name = req_strs[-2]
                user_password = req_strs[-1]
                r = modules.user.register(user_name, user_password)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(r)

        elif re.search(r'/stock/query/*', self.path) is not None:
            pass


class SimpleHttpServer:
    def __init__(self, ip, port):
        self.server_thread = None
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.waitForThread()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, sigint_handler)

    server = SimpleHttpServer(args.ip, args.port)
    server.start()
    sys.stderr.write("HTTP Server Running......\n")
    while not g_close:
        time.sleep(5)
    sys.stderr.write("Stopping HTTP Server......\n")
    server.stop()
