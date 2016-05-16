#!/usr/bin/env python3

import os
from ..validrequest import ValidRequestHandler
from gateway.base.pyjsonrpc import rpcresponse

class JsonrpcDeviceHandler(ValidRequestHandler):

    def post(self, did = None):
        if self.validate_jsonrpc():

            gateway = self.settings["gateway"]
            if did is not None:
                did = int(did)

            if self.rpcreq.method == "get_devices":
                resp = rpcresponse.Response(jsonrpc = "2.0", result = gateway.devices, id = self.rpcreq.id)
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.dumps().encode("utf-8"))

            elif self.rpcreq.method == "set_name":
                name = self.rpcreq.params.get("name")

                if did is None or name is None:
                    self.resp_unknow_error()
                else:
                    for dev in gateway.devices:
                        if dev["id"] == did:
                            dev["name"] = name
                            self.resp_success()
                            break
                    else:
                        self.resp_unknow_error()

            elif self.rpcreq.method == "get_name":
                if did is None:
                    self.resp_unknow_error()
                else:
                    for dev in gateway.devices:
                        if dev["id"] == did:
                            resp = rpcresponse.Response(jsonrpc = "2.0", result = dev["name"], id = self.rpcreq.id)
                            self.set_header("Content-Type", "application/json; charset=utf-8")
                            self.write(resp.dumps().encode("utf-8"))
                            break
                    else:
                        self.resp_unknow_error()

            elif self.rpcreq.method == "set_position":
                position = self.rpcreq.params.get("position")

                if did is None or position is None:
                    self.resp_unknow_error()
                else:
                    for dev in gateway.devices:
                        if dev["id"] == did:
                            dev["position"] = position
                            self.resp_success()
                            break
                    else:
                        self.resp_unknow_error()

            elif self.rpcreq.method == "get_position":
                if did is None:
                    self.resp_unknow_error()
                else:
                    for dev in gateway.devices:
                        if dev["id"] == did:
                            resp = rpcresponse.Response(jsonrpc = "2.0", result = dev["position"], id = self.rpcreq.id)
                            self.set_header("Content-Type", "application/json; charset=utf-8")
                            self.write(resp.dumps().encode("utf-8"))
                            break
                    else:
                        self.resp_unknow_error()

            else:
                self.resp_unknow_error()
        else:
            pass
