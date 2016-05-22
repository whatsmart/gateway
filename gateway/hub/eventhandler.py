#!/usr/bin/env python3

import os
from . import jsonrpchandler
from ..base import hipc, jsonrpc
from . import database

class HubEventHandler(jsonrpchandler.JsonrpcHandler):
    def listen_event(self, id = None):
        pass

    def report_event(self):
        assert self.params
        data = self.params.get("data")
        assert data
        did = data.get("id")
        assert did
        did = int(did)

        if self.params.get("name") == "device_state_changed":
            device = self.gateway.hub.get_device(did)
            if device:
                states = data.get("state")
                assert states
                for key in states.keys():
                    if key in device["state"].keys():
                        device["state"][k] = states[k]

                #@todo push to user
