#!/usr/bin/env python3

from gateway.base import jsonrpc

#req = jsonrpc.Request(jsonrpc = "2.0", method = "add_device").dumps()
#print(req)

req = jsonrpc.Request(jsonrpc = "2.0", method = "add_device", params = [1,2,3]).dumps()
print(req)

obj = jsonrpc.Request.loads(req)
print(obj.jsonrpc)
print(obj.method)
print(obj.params)
print(obj.id)

#resp = jsonrpc.Response(jsonrpc = "2.0", result = 5555555, id = 123).dumps()
resp = jsonrpc.Response(jsonrpc = "2.0", error = jsonrpc.Response.Error(code=2, message=3), id = 123).dumps()
print(resp)

obj = jsonrpc.Response.loads(resp)
print(obj.jsonrpc)
print(obj.result)
print(obj.error.code)
print(obj.error.message)
print(obj.error.data)
print(obj.id)
