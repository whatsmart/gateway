#!/usr/bin/env python3

import tornado.iostream
from ..base import hipc

class HubStream(tornado.iostream.IOStream):
    def __init__(self, socket, *args, **kwargs):
        super().__init__(socket)

        self.gateway = kwargs.get("gateway")
        self.hub = self.gateway.hub
        self.web = self.gateway.web
        self.parser = hipc.Parser()
        self.parser.done_callback = self.on_message
        self.read_until_close(streaming_callback = self.on_read)

    def on_read(self, data):
            print(data)
            self.parser.parse(data)

    def on_message(self, message):
        #request
        if isinstance(message, hipc.Request):
            print(message)
        elif isinstance(message, hipc.Response):
            net = message.forward()
            #net is component name
            if net:
                for c in self.components:
                    if c.name == net:
                        c["stream"].write(message.binary())
                        break
            #否则，该响应的请求是有本程序发出
            else:
                mid = int(message.dest)
                self.gateway.future_result(mid, message.body)
