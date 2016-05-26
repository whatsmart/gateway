#!/usr/bin/env python3

import os
import json
from ..validrequest import ValidRequestHandler
from gateway.base import jsonrpc
from ...database import user as dbuser
from gateway.base.database import client as dbclient

class JsonrpcPushHandler(ValidRequestHandler):

    def get_user_from_authtoken(self):
        token = self.request.headers.get("Auth-Token")
        if token:
            return self.conn.get_user_from_token(token)
        else:
            return None

    def resp_database_error(self):
        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "database error"), id = self.rpcreq.id).dumps()
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(resp.encode("utf-8"))

    def post(self, uid = None):
        if self.validate_jsonrpc():

            dbpath = os.path.join(self.settings["root"], "data/gateway.db")
            self.conn = dbuser.User(dbpath)
            self.dbclient = dbclient.Client(dbpath)

            device_token = self.request.headers.get("Device-Token")

            #设备token设置名称
            if self.rpcreq.method == "set_client_info":
                name = self.rpcreq.params.get("name")
                platform = self.rpcreq.params.get("platform")
                if name and platform and device_token:
                    if self.dbclient.set_client_info(device_token, name, platform):
                        self.resp_success()
                    else:
                        self.resp_database_error()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid name, platform or device-token"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #绑定用户和设备token
            elif self.rpcreq.method == "bind_user":
                user = self.get_user_from_authtoken()

                if user and device_token:
                    if self.dbclient.bind_user(device_token, user["username"]):
                        self.resp_success()
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "you should set_device_name first"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid user or device-token"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #解除用户和设备token的绑定
            elif self.rpcreq.method == "unbind_user":
                user = self.get_user_from_authtoken()

                if user and device_token:
                    ret = self.dbclient.unbind_user(device_token, user["username"])
                    if ret:
                        self.resp_success()
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "not binded"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid user or device-token"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            else:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid rpc method"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return
        else:
            self.set_status(400, "Bad Request")

    def on_finish(self):
        if hasattr(self, "conn"):
            pass
            self.conn.conn.close()
