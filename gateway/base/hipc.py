#!/usr/bin/env python3

import time
import binascii

class Parser(object):
    '''消息体可以为任意类型数据，除了消息体之外，其他所有自负均采用ascii码
    '''

    state_firstline = 1
    state_headers = 2
    state_body = 3
    state_done = 4

    def __init__(self):
        self.state = self.state_firstline
        self.message = None
        self.buffer = bytes()
        self.cursor = 0
        self.done_callback = None

    def parse(self, data):
        self.buffer += data
        if self.state == self.state_firstline:
            if self.buffer.find(b"\r\n") == -1:
                return
            if not self.buffer.startswith(b"HIPC"):
                index = self.buffer.find(b"HIPC")
                if index == -1:
                    self.buffer = bytearray()
                else:
                    self.buffer = self.buffer[index:]

            tp = self.buffer.partition(b"\r\n")
            if tp[1] == b"\r\n":
                self.buffer = tp[2]
                line = tp[0]

                words = line.split()
                if len(words) > 1:
                    if words[1] == b"request":
                        self.message = Request()
                        self.message.version = words[0].split(b"/")[1].decode("ascii")
                        self.message.resource = words[2].decode("ascii") if len(words) > 2 else ""
                        self.state = self.state_headers
                    elif words[1] == b"response":
                        self.message = Response()
                        self.message.version = words[0].split(b"/")[1].decode("ascii")
                        self.message.dest = words[2].decode("ascii") if len(words) > 2 else ""
                        self.state = self.state_headers
                else:
                    print("parse first line error")
                    pass

        if self.state == self.state_headers:
            lines = self.buffer.split(b"\r\n")

            for line in lines:
                p = self.buffer.find(b"\r\n")
                self.buffer = self.buffer[p+len(b"\r\n"):]
                if not line:
                    self.state = self.state_body
                    break
                else:
                    tp = line.partition(b":")
                    if tp[1] == b":" and tp[0].strip():
                        self.message.headers[tp[0].decode("ascii").strip()] = tp[2].decode("ascii").strip()
                    else:
                        print("parse header error")
                        self.state = self.state_firstline

        if self.state == self.state_body:
            length = int(self.message.headers.get("length"))
            checksum = int(self.message.headers.get("checksum"))
            buffer_length = len(self.buffer)

            if length is not None:
                if buffer_length >= length:
                    self.message.body = self.buffer[0:length]
                    self.buffer = self.buffer[length:]

                    if checksum is not None:
                        if checksum != binascii.crc32(self.message.body):
                            print("body checksum error")
                            self.state = self.state_firstline
                            self.parse(bytearray())
                        else:
                            self.state = self.state_done
                    else:
                        self.state = self.state_done
            else:
                self.state = self.state_firstline
                self.parse(bytearray())

        if self.state == self.state_done:
            if self.done_callback:
                self.state = self.state_firstline
                self.done_callback(self.message)
            if len(self.buffer) > 0:
                self.state = self.state_firstline
                self.parse(bytearray())

class Request(object):
    def __init__(self, resource = "", headers = {}, body = bytes(), version = "1.0"):
        self.version = version #str
        self.resource = resource #str
        self.headers = headers #dict, str: str
        self.body = body #bytes

    def forward(self, by):
        if self.headers.get("origin"):
            self.headers["origin"] += "@" + by
        else:
            self.headers["origin"] = "@" + by

    def bytes(self):
        s = ""
        s += "HIPC/" + (self.version if self.version else "1.0") + \
             " request" + (" " + self.resource if self.resource else "") + "\r\n"
        self.headers["length"] = str(len(self.body))
        self.headers["checksum"] = str(binascii.crc32(self.body))
        if self.headers:
            for k in self.headers.keys():
                s += k + ": " + self.headers[k] + "\r\n"
        s += "\r\n"

        return bytes(s, "ascii") + self.body

    def __str__(self):
        s = "HIPC Request\n"
        s += "version: " + self.version + "\n"
        s += "resource: " + self.resource + "\n"
        for k in self.headers.keys():
            s += k + ": " + self.headers[k] + "\n"

        return s

class Response(object):
    def __init__(self, dest = "", headers = {}, body = bytes(), version = "1.0"):
        self.version = version #str
        self.dest = dest
        self.headers = headers #dict, str, str
        self.body = body #bytes

    def forward(self):
        if self.dest:
            t = self.dest.rpartition("@")
            if t[1] == "@":
                self.dest = t[0]
                return t[2]
        return ""

    def bytes(self):
        s = ""
        s += "HIPC/" + (self.version if self.version else "1.0") + \
             " response" + (" " + self.dest if self.dest else "") + "\r\n"
        self.headers["length"] = str(len(self.body))
        self.headers["checksum"] = str(binascii.crc32(self.body))
        if self.headers:
            for k in self.headers.keys():
                s += k + ": " + self.headers[k] + "\r\n"
        s += "\r\n"

        return bytes(s, "ascii") + self.body

    def __str__(self):
        s = "HIPC Response\n"
        s += "version: " + self.version + "\n"
        s += "dest: " + self.dest + "\n"
        for k in self.headers.keys():
            s += k + ": " + self.headers[k] + "\n"

        return s
