#!/usr/bin/env python3

import os
import socket
import tornado.iostream

class HubServer():
    def __init__(self):
        if os.access("/tmp/hub_sock", os.F_OK):
            os.remove("/tmp/hub_sock")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        sock.bind("/tmp/hub_sock")
        sock.listen(50)
        self.hubio = tornado.iostream.IOStream(sock)
