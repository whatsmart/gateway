#!/usr/bin/env python3

import re
import tornado.iostream
from ..base import hipc
from ..base import jsonrpc

class HubStream(tornado.iostream.IOStream):
    def __init__(self, socket, *args, **kwargs):
        super().__init__(socket)

        self.gateway = kwargs.get("gateway")
        self.hub = self.gateway.hub
        self.web = self.gateway.web
        self.routes = kwargs.get("routes")
        self.parser = hipc.Parser()
        self.parser.done_callback = self.on_message
        self.read_until_close(streaming_callback = self.on_read)

    def on_read(self, data):
            self.parser.parse(data)

    def on_message(self, message):
        #request
        if isinstance(message, hipc.Request):
            max = 0
            r = None
            for route in self.routes:
                spres = message.resource.split("/")
                sprt = route[0].split("/")
                if len(spres) == len(sprt):
                    for i, prt in enumerate(sprt):
                        if not re.match(prt, spres[i]):
                            break
                    else:
                        if len(sprt) > max:
                            max = len(sprt)
                            r = route
                            break

            if r:
                match = re.match(r[0], message.resource)
                if match:
                    try:
                        rpc_request = jsonrpc.Request.loads(message.body.decode("utf-8"))
                    except Exception:
                        print("bad jsonrpc request")
                        rpc_response = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 0, message = "invalid jsonrpc request"), id = 0)
                    else:
                        kwargs = {
                            "gateway": self.gateway,
                            "stream": self,
                            "jsonrpc": rpc_request.jsonrpc,
                            "params": rpc_request.params,
                            "rpcid": rpc_request.id,
                        }

                        handler = r[1](**kwargs)
                        if hasattr(handler, rpc_request.method):
                            m = getattr(handler, rpc_request.method)
                            try:
                                groups = match.groups()
                                m(*groups)
                            finally:
                                pass
            '''
            req = jsonrpc.Request.loads(message.body.decode("utf-8"))
            if req.method == "add_device":
                dev = { "id": 3,
                        "cid": self.socket.fileno(),
                        "name": "unknow",
                        "position": "unknow",
                        "vender": req.params.get("vender"),
                        "uniqid": "er-fd-ef-gf-cv-df",
                        "hwversion": req.params.get("hwversion"),
                        "swversion": req.params.get("swversion"),
                        "type": req.params.get("lighting"),
                        "operations": req.params.get("operations") 
                       }
                self.hub.devices.append(dev)
                #print(self.hub.devices)
                body = jsonrpc.Response(jsonrpc = "2.0", result = None, id = req.id).dumps()
                resp = hipc.Response(body = body.encode("utf-8"))
                self.write(resp.bytes())
            '''
        elif isinstance(message, hipc.Response):
            nid = message.forward()
            #nid是网络id，hub中采用组件id
            if nid:
                for c in self.components:
                    if c.id == nid:
                        c["stream"].write(message.bytes())
                        break
            #否则，该响应的请求是有本程序发出
            else:
                mid = int(message.dest)
                self.gateway.future_result(mid, message.body)
