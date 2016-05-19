#!/usr/bin/env python3

import socket
import argparse
import sys
import json
from threading import Thread
from gateway.base import hipc
from gateway.base import jsonrpc

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect("/tmp/hub_sock")

def no_exit(self, status=0, message=None):
    if message:
        self._print_message(message, sys.stderr)

argparse.ArgumentParser.exit = no_exit

def sendcmd():
    while True:
        cmd = input(">>> ")
        if len(cmd.split()) == 0:
            continue
        if cmd.split()[0].strip() == "add_device":

            print("请输入设备的属性")
            vender = input("厂商：")
            uniqid = input("唯一ID：")
            hwversion = input("硬件版本：")
            swversion = input("软件版本：")
            dtype = input("类型：")
            operations = input("操作：")
            operations = operations.split()

            dev = {
                "vender": vender,
                "uniqid": uniqid,
                "hwversion": hwversion,
                "swversion": swversion,
                "type": dtype,
                "operations": operations
            }
            body = jsonrpc.Request(jsonrpc = "2.0", method = "add_device", params = dev, id = 1).dumps()
            req = hipc.Request(resource = "device", body = body.encode("utf-8"))
            sock.send(req.bytes())

        elif cmd.split()[0].strip() == "remove_device":

            parser = argparse.ArgumentParser()
            parser.add_argument("-d", dest="did", type=int, required=True, help="设备id")
            args = None
            try:
                args = parser.parse_args(cmd.split()[1:])
            except Exception:
                del args
                continue
            print(args.did)
            body = jsonrpc.Request(jsonrpc = "2.0", method = "remove_device", id = 1).dumps()
            req = hipc.Request(resource = "device/"+str(args.did), body = body.encode("utf-8"))
            sock.send(req.bytes())

            del args

        elif cmd.split()[0].strip() == "success":

            parser = argparse.ArgumentParser()
            parser.add_argument("-d", dest="dest", type=int, required=True, help="消息的来源标识，即请求中的origin")
            args = None
            try:
                args = parser.parse_args(cmd.split()[1:])
            except Exception:
                del args
                continue

            resp = hipc.Response(dest = str(args.dest), body = '{"jsonrpc": "2.0","result": "null0000000000", "id": 1}'.encode("utf-8"))
            sock.send(resp.bytes())

            del args

def display():
    req = hipc.Request(resource = "component", body = '{"jsonrpc": "2.0","method": "register_component","params":{"name": "zigbee link adapter", "type": "ZigbeeLinkAdapter"},"id": 1}'.encode("utf-8"))
    sock.send(req.bytes())
    while True:
        data = sock.recv(100)
        print(data)

dth = Thread(target = display)
dth.start()

sth = Thread(target = sendcmd)
sth.start()
