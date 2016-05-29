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
        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "数据库错误"), id = self.rpcreq.id).dumps()
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(resp.encode("utf-8"))

    def post(self, uid = None):
        if self.validate_jsonrpc():

            dbpath = os.path.join(self.settings["root"], "data/gateway.db")
            self.conn = dbuser.User(dbpath)
            self.dbclient = dbclient.Client(dbpath)

            device_token = self.request.headers.get("Device-Token")

            if not device_token:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "没有Device-Token"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))

            #设备token设置名称
            if self.rpcreq.method == "set_client_info":
                name = self.rpcreq.params.get("name")
                platform = self.rpcreq.params.get("platform")
                if name and platform:
                    if self.dbclient.set_client_info(device_token, name, platform):
                        self.resp_success()
                    else:
                        self.resp_database_error()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "参数不合法"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #绑定用户和设备token
            elif self.rpcreq.method == "bind_user":
                user = self.get_user_from_authtoken()

                if user:
                    if self.dbclient.bind_user(device_token, user["username"]):
                        self.resp_success()
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "您应先注册设备"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "您没有登录"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #解除用户和设备token的绑定
            elif self.rpcreq.method == "unbind_user":
                user = self.get_user_from_authtoken()

                if user:
                    ret = self.dbclient.unbind_user(device_token, user["username"])
                    if ret:
                        self.resp_success()
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "没有绑定"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "您没有登录"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            else:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "方法不存在"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return
        else:
            self.set_status(400, "Bad Request")

    def on_finish(self):
        if hasattr(self, "conn"):
            pass
            self.conn.conn.close()
