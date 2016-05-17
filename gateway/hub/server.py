#!/usr/bin/env python3

from .hubstream import HubStream
from tornado.ioloop import IOLoop
from tornado.netutil import bind_sockets, bind_unix_socket, add_accept_handler

class HubServer():
    def __init__(self, *args, **kwargs):
        self.loop = IOLoop.current()
        self.gateway = kwargs.get("gateway")
        self.components = []
        self.devices = [{
                        "id": 10,
                        "name": "unknow",
                        "position": "unknow",
                        "vender": "Obama",
                        "uniqid": "er-fd-ef-gf-cv-df",
                        "hwversion": "1.2",
                        "swversion": "2.0",
                        "type": "lighting",
                        "operations": ["power_on", "power_off", "get_color", "set_color", "get_brightness", "set_brightness"] 
                       },]

    def listen(self, port):
        if port:
            socks = bind_sockets(port)
            for sock in socks:
                add_accept_handler(sock, self.accept)
        else:
            self.sock = bind_unix_socket("/tmp/hub_sock", mode = 755)
            add_accept_handler(self.sock, self.accept)

    def accept(self, conn, address):
        stream = HubStream(conn, gateway = self.gateway)
        stream.set_close_callback(self.on_client_close)

        comp = {
            "id": conn.fileno(),
            "name": "unknow",
            "type": "unknow",
            "stream": stream
        }
        self.components.append(comp)

    def on_client_close(self):
        for i, comp in enumerate(self.components):
            if comp["stream"].closed():
                self.components.pop(i)
                break
