#!/usr/bin/env python3

import os
from gateway.base import jsonrpc
from tornado.web import RequestHandler

class ValidRequestHandler(RequestHandler):
    def resp_unknow_error(self):
        resp = jsonrpc.Response(jsonrpc = "2.0", error = rpcresponse.Response.Error(1, "unknow error", None), id = self.rpcreq.id)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(resp.dumps().encode("utf-8"))

    def resp_success(self):
        resp = jsonrpc.Response(jsonrpc = "2.0", result = True, id = self.rpcreq.id)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(resp.dumps().encode("utf-8"))

    def validate_jsonrpc(self):
        try:
            rpcreq = jsonrpc.Request.loads(self.request.body.decode("utf-8"))
        except Exception:
            return False
        else:
            if not rpcreq:
                return False
            else:
                self.rpcreq = rpcreq
                return True
