#!/usr/bin/env python3

from .hubstream import HubStream
from tornado.ioloop import IOLoop
from tornado.netutil import bind_sockets, bind_unix_socket, add_accept_handler

class HubServer(object):
    def __init__(self, routes, *args, **kwargs):
        self.loop = IOLoop.current()
        self.gateway = kwargs.get("gateway")
        self.listeners = []
        self.clients = []
        self.devices = [{
                        "id": 0,
                        "cid": 0,
                        "name": "未命名",
                        "position": "未设置",
                        "vender": "Obama",
                        "uniqid": "er-fd-ef-gf-cv-df",
                        "hwversion": "1.2",
                        "swversion": "2.0",
                        "type": "lighting",
                        "operations": ["power_on", "power_off", "get_color", "set_color", "get_brightness", "set_brightness", "get_state", "set_state"],
                        "state": {"power": "off", "color": 0xff3344, "brightness": 70}
                       },]
        self.routes = routes

    def get_device(self, did):
        for dev in self.devices:
            if dev["id"] == did:
                return dev
        return None

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

        client = {
            "id": conn.fileno(),
            "name": "unknow",
            "type": "unknow",
            "stream": stream
        }
        self.clients.append(client)

    def on_client_close(self):
        rm_client = []
        rm_device = []
        for client in self.clients:
            if client["stream"].closed():
                rm_client.append(id(client))
                for d in self.devices:
                    if d["cid"] == client["id"]:
                        rm_device.append(id(d))

        for cid in rm_client:
            if client in self.clients:
                if cid == id(client):
                    self.clients.remove(client)

        for did in rm_device:
            for d in self.devices:
                if id(d) == did:
                    self.devices.remove(d)
