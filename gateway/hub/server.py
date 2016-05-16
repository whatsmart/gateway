#!/usr/bin/env python3

import socket
import tornado.iostream
from tornado.ioloop import IOLoop
from tornado.netutil import bind_unix_socket, add_accept_handler

class HubServer():
    def __init__(self, *args, **kwargs):
        self.sock = bind_unix_socket("/tmp/hub_sock", mode = 755)
        self.loop = IOLoop.current()
        self.gateway = kwargs.get("gateway")
        self.clients = []
        add_accept_handler(self.sock, self.accept)

    def accept(self, conn, address):
        iostm = tornado.iostream.IOStream(conn)
        iostm.read_until_close(streaming_callback = self.data_come)
        self.clients.append((iostm, conn, address))

    def data_come(self, data):
        #print(data)
        for f in self.gateway.futures:
            f.set_result("i am back")
