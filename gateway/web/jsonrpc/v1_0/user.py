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
        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "数据库错误"), id = self.rpcreq.id).dumps()
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
                    user = self.conn.create_user(username, password)
                    if user:
                        resp = jsonrpc.Response(jsonrpc = "2.0", result = user, id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "用户已经存在"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "参数不合法"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #用户登陆
            elif self.rpcreq.method == "login":
                username = self.rpcreq.params.get("username")
                password = self.rpcreq.params.get("password")
                if username and password:
                    users = self.conn.get_users()

                    for u in users:
                        if username == u["username"]:
                            ret = self.conn.login_user(username, password)
                            if ret:
                                resp = jsonrpc.Response(jsonrpc = "2.0", result = ret, id = self.rpcreq.id).dumps()
                                self.set_header("Content-Type", "application/json; charset=utf-8")
                                self.write(resp.encode("utf-8"))
                            else:
                                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "密码错误"), id = self.rpcreq.id).dumps()
                                self.set_header("Content-Type", "application/json; charset=utf-8")
                                self.write(resp.encode("utf-8"))
                            break
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "用户不存在"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))

                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "参数不合法"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))

                return

            #用户注销
            elif self.rpcreq.method == "logout":
                user = self.get_user_from_authtoken()
                if user:
                    if self.conn.logout_user(user["id"]):
                        self.resp_success()
                    else:
                        self.resp_database_error()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "您没有登录"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            if uid is None:
                resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "请求没有指明用户id"), id = self.rpcreq.id).dumps()
                self.set_header("Content-Type", "application/json; charset=utf-8")
                self.write(resp.encode("utf-8"))
                return

            #删除用户
            if self.rpcreq.method == "delete_user":
                if self.conn.delete_user(uid):
                    self.resp_success()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "用户不存在"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #获取单个用户
            if self.rpcreq.method == "get_user":
                user = self.conn.get_user(uid)
                if user:
                    resp = jsonrpc.Response(jsonrpc = "2.0", result = user, id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "用户不存在"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                return

            #修改密码
            elif self.rpcreq.method == "update_password":
                password = self.rpcreq.params.get("password")
                if not password:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "参数不合法"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))
                else:
                    if self.conn.update_password(uid, password):
                        self.resp_success()
                    else:
                        resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "用户不存在"), id = self.rpcreq.id).dumps()
                        self.set_header("Content-Type", "application/json; charset=utf-8")
                        self.write(resp.encode("utf-8"))
                return

            #设置用户权限,需管理员权限
            elif self.rpcreq.method == "set_permission":
                perm = self.rpcreq.params
                if self.conn.set_permission(uid, perm):
                    self.resp_success()
                else:
                    resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code = 3, message = "用户不存在"), id = self.rpcreq.id).dumps()
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(resp.encode("utf-8"))

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
