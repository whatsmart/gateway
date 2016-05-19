#!/usr/bin/env python3

import os
from tornado.web import RequestHandler

class IndexHandler(RequestHandler):
    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), "template")

    def get(self):
        gateway = self.settings.get("gateway")

        devices = {}
        for dev in gateway.hub.devices:
            if dev.get("type") not in devices.keys():
                devices[dev.get("type")] = [dev]
            else:
                devices[dev.get("type")].append(dev)

        self.render("index.html", devices = devices);
