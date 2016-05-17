#!/usr/bin/env python3

import time
import binascii

class Parser(object):
    '''values in first line, header fields and field values are utf-8 strings,
    when parsing, convert bytes to utf-8 string, when serializing, convert them
    to bytes, message body can be any kind of data
    '''

    state_firstline = 1
    state_headers = 2
    state_body = 3
    state_done = 4

    def __init__(self):
        self.state = self.state_firstline
        self.message = None
        self.buffer = bytearray()
        self.cursor = 0
        self.done_callback = None

    #@params data should be bytes or bytearray
    def parse(self, data):
        self.buffer.extend(data)
        if self.state == self.state_firstline:
            if self.buffer.find("\r\n".encode("ascii")) == -1:
                return
            if not self.buffer.startswith("HIPC".encode("ascii")):
                index = self.buffer.find("HIPC".encode("ascii"))
                if index == -1:
                    self.buffer = bytearray()
                else:
                    self.buffer = self.buffer[index:]

            tp = self.buffer.partition("\r\n".encode("ascii"))
            if tp[1] == "\r\n".encode("ascii"):
                self.buffer = tp[2]
                line = tp[0]

                words = line.split()
                if len(words) > 1:
                    if words[1] == "request".encode("ascii"):
                        self.message = Request()
                        self.message.version = words[0].split("/".encode("ascii"))[1].decode("utf-8")
                        self.message.resource = words[2].decode("utf-8") if len(words) > 2 else ""
                        self.state = self.state_headers
                    elif words[1] == "response".encode("ascii"):
                        self.message = Response()
                        self.message.version = words[0].split("/".encode("ascii"))[1].decode("utf-8")
                        self.message.dest = words[2].decode("utf-8") if len(words) > 2 else ""
                        self.state = state_headers
                else:
                    print("parse first line error")
                    pass

        if self.state == self.state_headers:
            lines = self.buffer.split("\r\n".encode("ascii"))

            for line in lines:
                p = self.buffer.find("\r\n".encode("utf-8"))
                self.buffer = self.buffer[p+len("\r\n".encode("utf-8")):]
                if not line:
                    self.state = self.state_body
                    break
                else:
                    tp = line.partition(":".encode("ascii"))
                    if tp[1] == ":".encode("ascii") and tp[0].strip():
                        self.message.headers[tp[0].decode("utf-8").strip()] = tp[2].decode("utf-8").strip()
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
    def __init__(self, resource = "", headers = {}, body = "", version = "1.0"):
        self.version = version #str
        self.resource = resource #str
        self.headers = headers #dict, str: str
        self.body = body #str

    def forward(self, by):
        if self.headers.get("origin"):
            self.headers["origin"] += "@".encode("utf-8") + by.encode("utf-8")
        else:
            self.headers["origin"] = "@".encode("utf-8") + by.encode("utf-8")

    def binary(self):
        s = bytearray()
        s += "HIPC/".encode("ascii") + (self.version.encode("utf-8") if self.version else "1.0".encode("utf-8")) + " request".encode("ascii") + " ".encode("ascii") + self.resource.encode("utf-8") + "\r\n".encode("ascii")
        self.headers["length"] = str(len(self.body))
        self.headers["checksum"] = str(binascii.crc32(self.body))

        if self.headers:
            for k in self.headers.keys():
                s += k.encode("utf-8") + ": ".encode("ascii") + self.headers[k].encode("utf-8") + "\r\n".encode("ascii")

        s += "\r\n".encode("ascii") + self.body
        return s

    def __str__(self):
        s = "HIPC Request\n"
        s += "version: " + self.version + "\n"
        s += "resource: " + self.resource + "\n"
        for k in self.headers.keys():
            s += k + ": " + self.headers[k] + "\n"
        s += self.body.decode("utf-8")
        return s

class Response(object):
    def __init__(self, dest = "", headers = {}, body = "", version = "1.0"):
        self.version = version #str
        self.dest = dest
        self.headers = headers #dict, str, str
        self.body = body #str

    def forward(self):
        if self.dest:
            t = self.dest.rpartition("@")
            if t[1] == "@":
                self.dest = t[0]
                return t[2]
        return ""

    def binary(self):
        s = bytearray()
        s += "HIPC/".encode("ascii") + (self.version.encode("utf-8") if self.version else "1.0") + " response".encode("ascii") + " ".encode("ascii") + self.dest.encode("utf-8") + "\r\n".encode("ascii")
        self.headers["length"] = str(len(self.body))
        self.headers["checksum"] = str(binascii.crc32(self.body))
        if self.headers:
            for k in self.headers.keys():
                s += k.encode("utf-8") + ": ".encode("ascii") + self.headers[k].encode("utf-8") + "\r\n".encode("ascii")

        s += "\r\n".encode("ascii") + self.body
        return s

    def __str__(self):
        s = "HIPC Response\n"
        s += "version: " + self.version + "\n"
        s += "dest: " + self.dest + "\n"
        for k in self.headers.keys():
            s += k + ": " + self.headers[k] + "\n"
        s += self.body.decode("utf-8")
        return s
