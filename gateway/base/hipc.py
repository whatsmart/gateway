#!/usr/bin/env python3

import binascii

class HIPCParser(object):
    def __init__(self):
        self._state = "ready"
        self._type = ""
        self._version = ""
        self._resource = ""
        self._dest = "";
        self._headers = {}
        self._body = ""
        self._data = ""
        self._cursor = 0
        self._protocol = None

    def parse(self, data):
        self._data = self._data + data.decode("utf-8")
        if self._state == "ready":
            if self._data.find("\r\n") == -1:
                return
            if not self._data.startswith("HIPC"):
                index = self._data.find("HIPC")
                if index == -1:
                    self._data = ""
                else:
                    self._data = self._data[index:]  

            for index, c in enumerate(self._data):
                if c == "\n" and self._data[index-1] == "\r":
                    line = self._data[self._cursor:index]

                    if line.strip().startswith("HIPC"):
                        tags = line.split(" ")
                        self._version = tags[0].strip().split("/")[1].strip()
                        self._type = tags[1].strip()
                        if self._type == "request":
                            self._resource = tags[2].strip()
                        elif self._type == "response" and len(tags) > 2:
                            self._dest = tags[2].strip()
                    else:
                        if self._cursor != index - 1:
                            pair = line.strip().split(":")
                            self._headers[pair[0].strip()] = pair[1].strip()
                        elif self._cursor == index - 1:
                            self._state = "header_found"
                            self._cursor = index + 1
                            break;
                    self._cursor = index + 1

        if self._state == "header_found":
            length = int(self.get_header("length"))
            checksum = int(self.get_header("checksum"))
            try:
                assert(length and checksum)
            except AssertionError:
                self._headers["length"] = "0"
                self.get_ready()
                self.parse(bytes())
                
            if len(self._data) - self._cursor >= length:
                self._body = self._data[self._cursor:self._cursor+length]
                sum = binascii.crc32(self._body.encode("utf-8"))
                if sum != checksum:
                    self._data = self._data[4:]
                    self.parse(bytes())
                else:
                    self._state = "finished"
                    print(self._headers)
                    self._protocol.handle_ipc(self)

                    if len(self._data) - self._cursor > length:
                        self.get_ready()
                        self.parse(bytes())
                    else:
                        self.get_ready()


    def get_ready(self):
        length = int(self.get_header("length"))
        self._resource = ""
        self._body = ""
        if len(self._data) - self._cursor > length:
            self._data = self._data[self._cursor+length:]
        else:
            self._data = ""
        self._type = ""
        self._version = ""
        self._headers = {}
        self._cursor = 0
        self._state = "ready"

    def set_protocol(self, protocol):
        self._protocol = protocol

    def get_protocol(self):
        return self._protocol

    def get_version(self):
        return self._version

    def get_last_route(self):
        routes = self._dest.split("@")
        if len(routes) > 0:
            return routes[len(routes)-1]

    def get_dest(self):
        return self._dest

    def get_type(self):
        return self._type

    def get_resource(self):
        return self._resource

    def get_dest(self):
        return self._dest

    def get_header(self, name):
        return self._headers.get(name)

    def get_headers(self):
        return self._headers

    def get_body(self):
        return self._body

class HIPCRequestSerializer(object):
    def __init__(self, resource = "", version = "", headers = {}, body = ""):
        self._version = version #str
        self._resource = resource #str
        self._length = None
        self._checksum = None
        self._headers = headers #dict, str, str
        self._body = body #str

    def set_version(self, version):
        self._version = version

    def set_resource(self, resource):
        self._resource = resource

    def set_header(self, name, value):
        self._headers[name] = value

    def set_headers(self, headers):
        self._headers = headers

    def set_body(self, body):
        self._body = body

    def serialize(self):
        be = self._body.encode("utf-8")
        s = ""
        s += "HIPC/" + (self._version if self._version else "1.0") + " request" + (" " + self._resource if self._resource else "") + "\r\n"
        s += "length: " + str(len(be)) + "\r\n"
        s += "checksum: " + str(binascii.crc32(be)) + "\r\n"
        if self._headers:
            for k in self._headers.keys():
                s += k + ": " + self._headers[k] + "\r\n"
        s += "\r\n"
        s += self._body
        return s

    def get_binary(self):
        return self.serialize().encode("utf-8")

    def get_string(self):
        return self.serialize()

class HIPCResponseSerializer(object):
    def __init__(self, dest = "", version = "", headers = {}, body = ""):
        self._version = version #str
        self._dest = dest
        self._length = None
        self._checksum = None
        self._headers = headers #dict, str, str
        self._body = body #str

    def set_version(self, version):
        self._version = version

    def set_dest(self, dest):
        self._dest = dest

    def set_header(self, name, value):
        self._headers[name] = value

    def set_headers(self, headers):
        self._headers = headers

    def set_body(self, body):
        self._body = body

    def serialize(self):
        be = self._body.encode("utf-8")
        s = ""
        s += "HIPC/" + (self._version if self._version else "1.0") + " response" + (" " + self._dest if self._dest else "") + "\r\n"
        s += "length: " + str(len(be)) + "\r\n"
        s += "checksum: " + str(binascii.crc32(be)) + "\r\n"
        if self._headers:
            for k in self._headers.keys():
                if k != "length" and k != "checksum":
                    s += k + ": " + self._headers[k] + "\r\n"
        s += "\r\n"
        s += self._body
        return s

    def get_binary(self):
        return self.serialize().encode("utf-8")

    def get_string(self):
        return self.serialize()
