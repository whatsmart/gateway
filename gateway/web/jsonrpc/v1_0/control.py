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
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 2, message = "请求没有指明设备id"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                self.finish()
                return

            device = gateway.hub.get_device(int(did))

            if device is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 2, message = "设备可能已掉线，请刷新后查看"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                self.finish()
                return

            if not self.has_permission(device):
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 2, message = "您没有权限"), id = self.rpcreq.id).dumps()
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

                device_token = self.request.headers.get("Device-Token")

                if hasattr(resp, "result"):
                    if device["type"] == "lighting":
                        if rpcreq.method == "set_state":
                            pairs = {}
                            for key in rpcreq.params.keys():
                                device["state"][key] = rpcreq.params[key]
                                pairs[key] = rpcreq.params[key]

                            payload = {
                                "expired": 0,
                                "data": {
                                    "device_state_changed": {"id": did, "state": pairs}
                                }
                            }

                            if device_token:
                                gateway.push.push_to_all_except_devices(payload, [device_token])
                            else:
                                gateway.push.push_to_all(payload)

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
