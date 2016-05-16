#!/usr/bin/env python3

import os
from .pyjsonrpc import rpcrequest
from .pyjsonrpc import rpcresponse
from tornado.web import RequestHandler

class ValidRequestHandler(RequestHandler):
    def resp_unknow_error(self):
        resp = rpcresponse.Response(jsonrpc = "2.0", error = rpcresponse.Response.Error(1, "unknow error", None), id = self.rpcreq.id)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(resp.dumps().encode("utf-8"))

    def resp_success(self):
        resp = rpcresponse.Response(jsonrpc = "2.0", result = None, id = self.rpcreq.id)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(resp.dumps().encode("utf-8"))

    def validate_jsonrpc(self):
        try:
            rpcreq = rpcrequest.Request.loads(self.request.body.decode("utf-8"))
        except Exception:
            self.set_status(400, "Bad Request")
            return False
        else:
            self.rpcreq = rpcreq
            return True
