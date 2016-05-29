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

            #获取所有设备
            if self.rpcreq.method == "get_devices":
                resp = jsonrpc.Response(jsonrpc = "2.0", result = gateway.hub.devices, id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            if did is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "请求没有指明设备id"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            device = gateway.hub.get_device(int(did))

            if device is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "设备可能已掉线，请刷新后查看"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            #根据id获取特定设备
            if self.rpcreq.method == "get_device":
                resp = jsonrpc.Response(jsonrpc = "2.0", result = device, id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            #获取设备的描述信息：名称，位置
            elif self.rpcreq.method == "get_info":
                if "name" not in self.rpcreq.params and "position" not in self.rpcreq.params:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "参数不合法"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    ret = {}
                    for field in self.rpcreq.params:
                        if field in device.keys():
                            ret[field] = device[field]

                    resp = jsonrpc.Response(jsonrpc = "2.0", result = ret, id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))

                return

            elif self.rpcreq.method == "set_info":
                if "name" not in self.rpcreq.params.keys() and "position" not in self.rpcreq.params.keys():
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "参数不合法"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    # @todo update name, position in database
                    name = self.rpcreq.params.get("name")
                    position = self.rpcreq.params.get("position")

                    if name:
                        device["name"] = name
                    if position:
                        device["position"] = position

                    self.resp_success()

                return

            else:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 1, message = "方法不存在"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return
        else:
            self.set_status(400, "Bad Request")
