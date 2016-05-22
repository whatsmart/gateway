#!/usr/bin/env python3

import json

class Request(object):
    def __init__(self, jsonrpc = None, method = None, **kwargs):
        self.jsonrpc = jsonrpc
        self.method = method
        self.kwargs = kwargs

    def dumps(self):
        assert self.jsonrpc is not None and self.method is not None
        d = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
        }
        if self.kwargs.get("params"):
            d["params"] = self.kwargs.get("params")
        if self.kwargs.get("id"):
            d["id"] = self.kwargs.get("id")

        s = json.dumps(d)

        return s

    @classmethod
    def loads(cls, req):
        try:
            d = json.loads(req)
        except ValueError:
            return None
        else:
            obj = cls()
            obj.kwargs.update(d)
            try:
                obj.jsonrpc = obj.kwargs.pop("jsonrpc")
                obj.method = obj.kwargs.pop("method")
            except KeyError:
                return None
            else:
                return obj

    def __getattr__(self, attr):
        if attr in self.kwargs.keys():
            return self.kwargs.get(attr)
        raise AttributeError

class Response(object):

    class Error(object):
        def __init__(self, code = None, message = None, data = None):
            assert code is not None and message is not None
            self.code = code
            self.message = message
            self.data = data

        def __getattr__(self, attr):
            if attr == "data":
                return self.data
            else:
                return None

    def __init__(self, jsonrpc = None, id = None, **kwargs):
        self.jsonrpc = jsonrpc
        self.id = id
        self.kwargs = kwargs

    def dumps(self):
        assert self.jsonrpc is not None and self.id is not None
        d = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }

        result = self.kwargs.get("result")
        error = self.kwargs.get("error")

        if "result" in self.kwargs.keys():
            d["result"] = result
        elif "error" in self.kwargs.keys():
            d["error"] = {
                "code": error.code,
                "message": error.message
            }
            if error.data:
                d["error"]["data"] = error.data

        return json.dumps(d)

    @classmethod
    def loads(cls, resp):
        try:
            d = json.loads(resp)
        except ValueError:
            return None
        else:
            obj = cls()
            obj.kwargs.update(d)
            if obj.kwargs.get("error"):
                try:
                    error = cls.Error(obj.kwargs["error"].pop("code"), obj.kwargs["error"].pop("message"))
                except KeyError:
                    return None
                if obj.kwargs["error"].get("data"):
                    error.data = obj.kwargs["error"]["data"]
                obj.kwargs["error"] = error
            try:
                obj.jsonrpc = obj.kwargs.pop("jsonrpc")
                obj.id = obj.kwargs.pop("id")
            except KeyError:
                return None
            else:
                return obj

    def __getattr__(self, attr):
        if attr in self.kwargs.keys():
            return self.kwargs.get(attr)
        raise AttributeError
