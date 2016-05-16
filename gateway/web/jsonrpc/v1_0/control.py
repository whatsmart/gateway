#!/usr/bin/env python3

import os
import time
from tornado import gen
from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from tornado.gen import with_timeout, TimeoutError
from ..validrequest import ValidRequestHandler
from gateway.base.pyjsonrpc import rpcresponse

class JsonrpcControlHandler(ValidRequestHandler):
    @gen.coroutine
    def post(self, did = None):
        if self.validate_jsonrpc():

            gateway = self.settings["gateway"]
            if did is not None:
                did = int(did)

            if self.rpcreq.method == "power_on":
                fut = Future()
                gateway.add_future(fut)

                try:
                    yield with_timeout(time.time() + 10, fut)
                except TimeoutError:
                    print("timeout")
                    self.set_status(504, "Gateway Timeout")
                else:
                    hub_resp = fut.result()
                
                    resp = rpcresponse.Response(jsonrpc = "2.0", result = hub_resp, id = self.rpcreq.id)
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(hub_resp.encode("utf-8"))
                finally:
                    gateway.remove_future(fut)
                    self.finish()

            else:
                self.resp_unknow_error()
        else:
            pass
