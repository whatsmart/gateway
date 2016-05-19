#!/usr/bin/env python3

from .hubstream import HubStream
from tornado.ioloop import IOLoop
from tornado.netutil import bind_sockets, bind_unix_socket, add_accept_handler

class HubServer(object):
    def __init__(self, routes, *args, **kwargs):
        self.loop = IOLoop.current()
        self.gateway = kwargs.get("gateway")
        self.components = []
        self.devices = [{
                        "id": 10,
                        "cid": 0,
                        "name": "unknow",
                        "position": "unknow",
                        "vender": "Obama",
                        "uniqid": "er-fd-ef-gf-cv-df",
                        "hwversion": "1.2",
                        "swversion": "2.0",
                        "type": "lighting",
                        "operations": ["power_on", "power_off", "get_color", "set_color", "get_brightness", "set_brightness"] 
                       },]
        self.routes = routes

    def listen(self, port):
        if port:
            socks = bind_sockets(port)
            for sock in socks:
                add_accept_handler(sock, self.accept)
        else:
            self.sock = bind_unix_socket("/tmp/hub_sock", mode = 755)
            add_accept_handler(self.sock, self.accept)

    def accept(self, conn, address):
        stream = HubStream(conn, routes = self.routes, gateway = self.gateway)
        stream.set_close_callback(self.on_client_close)

        comp = {
            "id": conn.fileno(),
            "name": "unknow",
            "type": "unknow",
            "stream": stream
        }
        self.components.append(comp)

    def on_client_close(self):
        rm_comp = []
        rm_device = []
        for comp in self.components:
            if comp["stream"].closed():
                rm_comp.append(comp)

        for c in rm_comp:
            for d in self.devices:
                if d["cid"] == c["id"]:
                    rm_device.append(d)
        
        for c in self.components:
            if c in rm_comp:
                self.components.remove(c)

        for d in enumerate(self.devices):
            if d in rm_device:
                self.devices.remove(d)
