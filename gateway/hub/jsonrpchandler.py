#!/usr/bin/env python3

class JsonrpcHandler(object):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
