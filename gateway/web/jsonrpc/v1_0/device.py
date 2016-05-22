#!/usr/bin/env python3

import os
from ..validrequest import ValidRequestHandler
from gateway.base import jsonrpc
from gateway.web import database

class JsonrpcDeviceHandler(ValidRequestHandler):

    def post(self, did = None):
        if self.validate_jsonrpc():
            gateway = self.settings["gateway"]
            device = None

            if self.rpcreq.method == "get_devices":
                resp = jsonrpc.Response(jsonrpc = "2.0", result = gateway.hub.devices, id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            if did is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "without a device id in url"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            for dev in gateway.hub.devices:
                if dev["id"] == int(did):
                    device = dev
                    break

            if device is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "can't find the device with that id"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            if self.rpcreq.method == "set_name":
                name = self.rpcreq.params.get("name")
                if not name:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "need a string"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    # @todo update name in database
                    device["name"] = name
                    self.resp_success()
                return

            elif self.rpcreq.method == "get_name":
                resp = jsonrpc.Response(jsonrpc = "2.0", result = device["name"], id = self.rpcreq.id)
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.dumps().encode("utf-8"))
                return

            elif self.rpcreq.method == "set_position":
                position = self.rpcreq.params.get("position")

                if not position:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "need a string"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    # @todo update position in database
                    device["position"] = position
                    self.resp_success()
                return

            elif self.rpcreq.method == "get_position":
                resp = jsonrpc.Response(jsonrpc = "2.0", result = device["position"], id = self.rpcreq.id)
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.dumps().encode("utf-8"))
                return

            elif self.rpcreq.method == "get_device":
                resp = jsonrpc.Response(jsonrpc = "2.0", result = device, id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            else:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "invalid rpc method"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return
        else:
            self.set_status(400, "Bad Request")
