#!/usr/bin/env python3

import os
from tornado.web import RequestHandler

class DeviceHandler(RequestHandler):
    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), "template")

    def get(self, did = None):
        gateway = self.settings.get("gateway")

        devices = {}
        for dev in gateway.hub.devices:
            if dev.get("type") not in devices.keys():
                devices[dev.get("type")] = [dev]
            else:
                devices[dev.get("type")].append(dev)

        if did is None:
            self.render("device.html", devices = devices);
        else:
            device = None
            for dev in gateway.hub.devices:
                if dev.get("id") == int(did):
                    device = dev
                    break
            if device is not None:
                self.render("device_lighting.html", devices = devices, device = device)
            else:
                self.set_status(404, "Not Found")
                self.write("设备可能掉线了")
