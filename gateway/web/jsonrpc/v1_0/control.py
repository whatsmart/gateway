#!/usr/bin/env python3

import os
import time
from tornado import gen
from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from tornado.gen import with_timeout, TimeoutError
from ..validrequest import ValidRequestHandler
from gateway.base import jsonrpc
from gateway.base import hipc

class JsonrpcControlHandler(ValidRequestHandler):
    def has_permission(self, device):
        return True

    @gen.coroutine
    def post(self, did = None):
        if self.validate_jsonrpc():
            gateway = self.settings["gateway"]
            device = None

            if did is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 2, message = "without a device id in url"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                self.finish()
                return

            for dev in gateway.hub.devices:
                if dev["id"] == int(did):
                    device = dev
                    break

            if device is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 2, message = "can't find the device with that id"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                self.finish()
                return

            if not self.has_permission(device):
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 2, message = "you don't hava permission"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                self.finish()
                return

            fut = Future()
            gateway.add_future(fut)

            #将请求转发给设备的管理者,self.request.body为jsonrpc格式，直接转发
            hipc_request = hipc.Request(resource = "control/" + str(did), headers = {"origin": str(id(fut))}, body = self.request.body)
            for client in gateway.hub.clients:
                if device["cid"] == client["id"]:
                    client["stream"].write(hipc_request.bytes())
                    break

            try:
                yield with_timeout(time.time() + 20, fut)
            except TimeoutError:
                self.set_status(504, "Gateway Timeout")
            else:
                hub_resp = fut.result()
                assert hub_resp
                resp = jsonrpc.Response.loads(hub_resp.decode("utf-8"))
                rpcreq = jsonrpc.Request.loads(self.request.body.decode("utf-8"))

                if hasattr(resp, "result"):
                    if device["type"] == "lighting":
                        if rpcreq.method == "power_on":
                            device["state"]["power"] = "on"

                        elif rpcreq.method == "power_off":
                            device["state"]["power"] = "off"

                        elif rpcreq.method == "set_color":
                            assert type(rpcreq.params.get("color")) == int
                            device["state"]["color"] = rpcreq.params.get("color")

                        elif rpcreq.method == "get_color":
                            assert type(resp.result) == int
                            device["state"]["color"] = resp.result

                        elif rpcreq.method == "set_brightness":
                            assert type(rpcreq.params.get("brightness")) == int
                            device["state"]["brightness"] = rpcreq.params.get("brightness")

                        elif rpcreq.method == "get_brightness":
                            assert type(resp.result) == int
                            device["state"]["brightness"] = resp.result

                        elif rpcreq.method == "set_state":
                            for key in rpcreq.params.keys():
                                if key in device["state"].keys():
                                    device["state"][key] = rpcreq.params[key]

                        elif rpcreq.method == "get_state":
                            for key in resp.result.keys():
                                if key in device["state"].keys():
                                    device["state"][key] = resp.result[key]

                elif hasattr(resp, "error"):
                    pass

                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(hub_resp)

            finally:
                gateway.remove_future(fut)
                self.finish()
        else:
            self.set_status(400, "Bad Request")
            self.finish()
