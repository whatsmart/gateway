#!/usr/bin/env python3

import os
import json
from ..validrequest import ValidRequestHandler
from gateway.base.pyjsonrpc import rpcresponse
from ...database import user as dbuser

class JsonrpcUserHandler(ValidRequestHandler):

    def get_user_from_authtoken(self):
        token = self.request.headers.get("Auth-Token")
        if token:
            return self.conn.get_user_from_token(token)
        else:
            return None

    def add_user(self, username, password):
        if username and password:
            if self.conn.create_user(username, password):
                self.resp_success()
            else:
                self.resp_unknow_error()

    def delete_user(self, uid):
        if self.conn.delete_user(uid):
            self.resp_success()
        else:
            self.resp_unknow_error()

    def update_password(self, uid, password):
        if self.conn.update_password(uid, password):
            self.resp_success()
        else:
            self.resp_unknow_error()

    def get_users(self):
        users = self.conn.get_users()

        if isinstance(users, list):
            resp = rpcresponse.Response(jsonrpc = "2.0", result = users, id = self.rpcreq.id)
            self.set_header("Content-Type", "application/json; charset=utf-8")
            self.write(resp.dumps().encode("utf-8"))
        else:
            self.resp_unknow_error()

    def login_user(self, username, password):
        ret = self.conn.login_user(username, password)
        if ret:
            resp = rpcresponse.Response(jsonrpc = "2.0", result = ret, id = self.rpcreq.id)
            self.set_header("Content-Type", "application/json; charset=utf-8")
            self.write(resp.dumps().encode("utf-8"))
        else:
            self.resp_unknow_error()

    def logout_user(self, uid):
        ret = self.conn.logout_user(uid)
        if ret:
            self.resp_success()
        else:
            self.resp_unknow_error()

    def set_permission(self, uid, perm):
        if self.conn.set_permission(uid, perm):
            self.resp_success()
        else:
            self.resp_unknow_error()

    def post(self, path = None):
        if self.validate_jsonrpc():

            dbpath = os.path.join(self.settings["root"], "data/gateway.db")
            self.conn = dbuser.User(dbpath)

            #添加用户
            if self.rpcreq.method == "add_user":
                username = self.rpcreq.params.get("username")
                password = self.rpcreq.params.get("password")
                self.add_user(username, password)

            #删除用户
            elif self.rpcreq.method == "delete_user":
                if path is not None:
                    uid = int(path)
                    self.delete_user(uid)
                else:
                    self.resp_unknow_error()

            #修改密码
            elif self.rpcreq.method == "update_password":
                password = self.rpcreq.params.get("password")
                if path is not None and password:
                    uid = int(path)
                    
                    self.update_password(uid, password)
                else:
                    self.resp_unknow_error()

            #获取所有用户
            elif self.rpcreq.method == "get_users":
                self.get_users()

            #用户登陆
            elif self.rpcreq.method == "login":
                username = self.rpcreq.params.get("username")
                password = self.rpcreq.params.get("password")
                if username and password:
                    self.login_user(username, password)
                else:
                    self.resp_unknow_error()

            #用户注销
            elif self.rpcreq.method == "logout":
                user = self.get_user_from_authtoken()
                if user:
                    self.logout_user(user["id"])
                else:
                    self.resp_unknow_error()

            #设置用户权限,需管理员权限
            elif self.rpcreq.method == "set_permission":
                if path is not None:
                    uid = int(path)
                    perm = self.rpcreq.params.get("permission")
                    self.set_permission(uid, perm)
                else:
                    self.resp_unknow_error()

            else:
                self.resp_unknow_error()
        else:
            pass

    def on_finish(self):
        if hasattr(self, "conn"):
            self.conn.conn.close()
