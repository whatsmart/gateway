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
                payload = {
                    "expired": 0,
                    "data": {
                        "device_state_changed": {"id": did, "state": {}}
                    }
                }

                for key in states.keys():
                    device["state"][key] = states[key]
                    payload["data"]["device_state_changed"]["state"][key] = states[key]

                self.gateway.push.push_to_all(payload)
