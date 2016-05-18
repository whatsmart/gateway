#!/usr/bin/env python3

import os
import json
from ..validrequest import ValidRequestHandler
from gateway.base import jsonrpc
from ...database import user as dbuser

class JsonrpcUserHandler(ValidRequestHandler):

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

            #获取所有用户
            if self.rpcreq.method == "get_users":
                users = self.conn.get_users()
                if users:
                    resp = jsonrpc.Response(jsonrpc = "2.0", result = users, id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    self.resp_database_error()
                return

            #添加用户
            elif self.rpcreq.method == "add_user":
                username = self.rpcreq.params.get("username")
                password = self.rpcreq.params.get("password")
                if username and password:
                    if self.conn.create_user(username, password):
                        self.resp_success()
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "username already exists"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid username or password"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            if uid is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "without uid in url"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            #删除用户
            if self.rpcreq.method == "delete_user":
                if self.conn.delete_user(uid):
                    self.resp_success()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "user doesn't exists"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #修改密码
            elif self.rpcreq.method == "update_password":
                password = self.rpcreq.params.get("password")
                if not password:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid password"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    if self.conn.update_password(uid, password):
                        self.resp_success()
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "user doesn't exists"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                return

            #用户登陆
            elif self.rpcreq.method == "login":
                username = self.rpcreq.params.get("username")
                password = self.rpcreq.params.get("password")
                if username and password:
                    ret = self.conn.login_user(username, password)
                    if ret:
                        resp = jsonrpc.Response(jsonrpc = "2.0", result = ret, id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "username or password wrong"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid username or password"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #用户注销
            elif self.rpcreq.method == "logout":
                user = self.get_user_from_authtoken()
                if user:
                    self.conn.logout_user(user["id"])
                    self.resp_success()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "you are not logged in current"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #设置用户权限,需管理员权限
            elif self.rpcreq.method == "set_permission":
                perm = self.rpcreq.params.get("permission")
                if self.conn.set_permission(uid, perm):
                    self.resp_success()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "user doesn't exists"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))

            else:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "invalid rpc method"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

    def on_finish(self):
        if hasattr(self, "conn"):
            self.conn.conn.close()
