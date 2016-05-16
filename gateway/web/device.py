#!/usr/bin/env python3

import os
from tornado.web import RequestHandler

class DeviceHandler(RequestHandler):
    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), "template")

    def get(self):
        self.render("device.html");
