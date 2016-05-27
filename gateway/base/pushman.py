#!/usr/bin/env python3

"""payload是字典格式,定义与push.py，pushman采用“个推”提供的接口。
push中定义的字段个推不能完全支持。notification和data分别代表通知
和数据透传。


#个推支持情况                                     android         ios

{
    "targets": [
        ["deviceid", "platform"],
        ...
    ],
    "options": {
        "expired": 3600,                           支持
    }
    "notification": {
        "title": "notification title",             支持          
        "body": "notification content",            支持          支持
    }
    "data": {                                      支持          支持
        "device_state_changed": {
            "id": 123
        }
        "message_arrived": {
            "id": 22
        }
    }
}
"""

import os
import json
from . import push
from .database import client as app_client
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

class PushMan(push.Push):

    def __init__(self, server):
        dbpath = os.path.join(os.path.split(os.path.dirname(__file__))[0],
                              "data/gateway.db")
        self.db = app_client.Client(dbpath)
        self.server = server + "/push"

    @gen.coroutine
    def push_to_all(self, payload):
        if not payload.get("targets"):
            payload["targets"] = []
        clients = self.db.get_clients()
        if clients:
            for client in clients:
                #append tuple(deviceid, platform)
                payload["targets"].append((client["deviceid"], client["platform"]))

            request = HTTPRequest(self.server)
            request.method = "POST"
            request.headers = {"Content-Type": "application/json; charset=utf-8"}
            request.body = json.dumps(payload)

            httpclient = AsyncHTTPClient()
            response = yield httpclient.fetch(request)
            #print(response.body.decode("utf-8"))

    @gen.coroutine
    def push_to_all_except_users(self, payload, usernames):
        """除了usernames中包含的username
        """
        if not payload.get("targets"):
            payload["targets"] = []
        clients = self.db.get_clients()
        if clients:
            for client in clients:
                if client["username"] not in usernames:
                    payload["targets"].append((client["deviceid"], client["platform"]))

            request = HTTPRequest(self.server)
            request.method = "POST"
            request.headers = {"Content-Type": "application/json; charset=utf-8"}
            request.body = json.dumps(payload)

            httpclient = AsyncHTTPClient()
            response = yield httpclient.fetch(request)
            #print(response.body.decode("utf-8"))

    @gen.coroutine
    def push_to_all_except_devices(self, payload, deviceids):
        """除了deviceids中包含的deviceid
        """
        if not payload.get("targets"):
            payload["targets"] = []
        clients = self.db.get_clients()
        if clients:
            for client in clients:
                if client["deviceid"] not in deviceids:
                    payload["targets"].append((client["deviceid"], client["platform"]))

            request = HTTPRequest(self.server)
            request.method = "POST"
            request.headers = {"Content-Type": "application/json; charset=utf-8"}
            request.body = json.dumps(payload)

            httpclient = AsyncHTTPClient()
            response = yield httpclient.fetch(request)
            #print(response.body.decode("utf-8"))

    @gen.coroutine
    def push_to_user(self, payload, username):
        if not payload.get("targets"):
            payload["targets"] = []
        clients = self.db.get_clients_by_username(username)
        if clients:
            for client in clients:
                payload["targets"].append((client["deviceid"], client["platform"]))

            request = HTTPRequest(self.server)
            request.method = "POST"
            request.headers = {"Content-Type": "application/json; charset=utf-8"}
            request.body = json.dumps(payload)

            httpclient = AsyncHTTPClient()
            response = yield httpclient.fetch(request)
            #print(response.body.decode("utf-8"))

    @gen.coroutine
    def push_to_device(self, payload, deviceid):
        if not payload.get("targets"):
            payload["targets"] = []
        client = self.db.get_client_by_deviceid(deviceid)
        if client:
            payload["targets"] = [(client["deviceid"], client["platform"])]

            request = HTTPRequest(self.server)
            request.method = "POST"
            request.headers = {"Content-Type": "application/json; charset=utf-8"}
            request.body = json.dumps(payload)

            httpclient = AsyncHTTPClient()
            response = yield httpclient.fetch(request)
            #print(response.body.decode("utf-8"))
