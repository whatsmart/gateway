#!/usr/bin/env python3

import os
from . import jsonrpchandler
from ..base import hipc, jsonrpc
from . import database

class HubDeviceHandler(jsonrpchandler.JsonrpcHandler):
    def remove_device(self, id = None):
        assert id
        id = int(id)
        for i, dev in enumerate(self.gateway.hub.devices):
            if dev["id"] == id:
                self.gateway.hub.devices.pop(i)
                break
        else:
            body = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "device not found"), id = self.rpcid).dumps()
            resp = hipc.Response(body = body.encode("utf-8"))
            self.stream.write(resp.bytes())
            return

        body = jsonrpc.Response(jsonrpc = "2.0", result = None, id = self.rpcid).dumps()
        resp = hipc.Response(body = body.encode("utf-8"))
        self.stream.write(resp.bytes())

    def add_device(self):
        assert self.params
        dbpath = os.path.join(self.gateway.root, "data/gateway.db")
        db = database.Device(dbpath)

        did = db.add_device(self.params.get("uniqid"))

        dev = { "id": did,
            "cid": self.stream.socket.fileno(),
            "name": "未命名",
            "position": "未设置",
            "vender": self.params.get("vender"),
            "uniqid": self.params.get("uniqid"),
            "hwversion": self.params.get("hwversion"),
            "swversion": self.params.get("swversion"),
            "type": self.params.get("type"),
            "operations": self.params.get("operations"),
            "state": self.params.get("state") or {}
        }

        self.gateway.hub.devices.append(dev)
        body = jsonrpc.Response(jsonrpc = "2.0", result = did, id = self.rpcid).dumps()
        resp = hipc.Response(body = body.encode("utf-8"))
        self.stream.write(resp.bytes())
