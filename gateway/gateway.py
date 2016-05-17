#!/usr/bin/env python3

import os
import getopt
import sys
import tornado.web
import gateway.hub.server
from tornado.ioloop import IOLoop

from .web.index import IndexHandler
from .web.device import DeviceHandler
from .web.jsonrpc.v1_0.device import JsonrpcDeviceHandler
from .web.jsonrpc.v1_0.user import JsonrpcUserHandler
from .web.jsonrpc.v1_0.control import JsonrpcControlHandler

class Gateway(object):
    """设备是一个字典列表，每个设备由一个字典表示
    device["id"] 设备在系统中的id，为动态生成
    device["name"] 设备的名称，保存在数据库中，根据uniqid检索
    device["position"] 设备的位置，保存在数据库中，根据uniqid检索
    device["vender"] 设备厂商
    device["uniqid"] 唯一id，为设备的mac地址
    device["hwversion"] 硬件版本
    device["swversion"] 软件版本
    device["type"] 设备类型，如lighting、Camera
    device["operations"] 支持的操作方法，如“power_on”，该值为列表，如["power_on", "set_color", ...]
    """

    def __init__(self, hubport = None, webport = 80):
        self.loop = IOLoop.instance()
        self.futures = []
        self.hub = gateway.hub.server.HubServer(gateway = self)
        self.hub.listen(hubport)
        self.web = tornado.web.Application(
            [
                (r"/", IndexHandler),
                (r"/device", DeviceHandler),
                (r"/jsonrpc/v1.0/device", JsonrpcDeviceHandler),
                (r"/jsonrpc/v1.0/device/(\d+)", JsonrpcDeviceHandler),
                (r"/jsonrpc/v1.0/control/(\d+)", JsonrpcControlHandler),
                (r"/jsonrpc/v1.0/user", JsonrpcUserHandler),
                (r"/jsonrpc/v1.0/user/(\d+)", JsonrpcUserHandler),
            ], gateway = self, root = os.path.dirname(__file__))
        self.web.listen(webport)

    def add_future(self, fut):
        self.futures.append(fut)

    def remove_future(self, fut):
        for i, f in enumerate(self.futures):
            if f is fut:
                self.futures.pop(i)

    def future_result(self, fid, result):
        fid = int(fid)
        for f in self.futures:
            if fid == id(f):
                f.set_result(result)

    def run(self):
        self.loop.start()

if __name__ == "__main__":
    optlist, args = getopt.getopt(sys.argv[1:], "h:w:")
    hubport = None
    webport = 80
    for opt in optlist:
        if "h" in opt[0]:
            hubport = int(opt[1])
        if "w" in opt[0]:
            webport = int(opt[1])

    gateway = Gateway(hubport = hubport, webport = webport)

    gateway.run()
