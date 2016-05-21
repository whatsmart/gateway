#!/usr/bin/env python3

import gi
import socket
import sys
import threading
import selectors
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gateway.base import hipc, jsonrpc

class LightingClient(object):
    def __init__(self):
        self.did = None
        self.sock = None
        self.sel = selectors.SelectSelector()
        self.builder = Gtk.Builder.new_from_file("lighting.ui")
        self.window = self.builder.get_object("window")
        self.window.connect("delete_event", self.exit)
        self.window.set_title("模拟智能灯")
        self.btn_color = self.builder.get_object("btn_color")
        self.btn_color.connect("clicked", self.color_changed)
        self.btn_brightness = self.builder.get_object("btn_brightness")
        self.btn_brightness.connect("clicked", self.brightness_changed)
        self.btn_connect = self.builder.get_object("connect")
        self.btn_connect.connect("clicked", self.connect_server)
        self.btn_disconnect = self.builder.get_object("disconnect")
        self.btn_disconnect.connect("clicked", self.disconnect_server)
        self.uniqid_entry = self.builder.get_object("uniqid")
        self.uniqid_entry.set_text("ae-3d-12-5f-bc-43")
        self.vender_entry = self.builder.get_object("vender")
        self.vender_entry.set_text("whatsmart")
        self.hwversion_entry = self.builder.get_object("hwversion")
        self.hwversion_entry.set_text("1.2")
        self.swversion_entry = self.builder.get_object("swversion")
        self.swversion_entry.set_text("2.3")
        self.power_switch = self.builder.get_object("power")
        self.power_switch.set_active(False)
        self.color_entry = self.builder.get_object("color")
        self.color_entry.set_text(hex(0))
        self.brightness_entry = self.builder.get_object("brightness")
        self.brightness_entry.set_text(str(0))
        self.sock_type = self.builder.get_object("sock_type")
        self.sock_type.connect("changed", self.toggle_sock_port)
        self.sock_addr = self.builder.get_object("sock_addr")
        self.sock_port = self.builder.get_object("sock_port")
        self.port_box = self.builder.get_object("port_box")

        self.stop = False
        self.parser = hipc.Parser()
        self.parser.done_callback = self.handle_message

    def toggle_sock_port(self, combo):
        value = combo.get_active()
        if value == 0:
            self.port_box.hide()
            self.sock_addr.set_text("/tmp/hub_sock")
        elif value == 1:
            self.sock_addr.set_text("121.42.156.167")
            self.sock_port.set_text("8080")
            self.port_box.show()

    def power_changed(self, button):
        if self.sock:
            active = self.power_switch.get_active()
            if active:
                state = "on"
            else:
                state = "off"

            params = {
                "name": "device_status_changed",
                "data": {
                    "id": self.did,
                    "status": {
                        "power": state
                    }                
                }
            }

            body = jsonrpc.Request(jsonrpc = "2.0", method="report_event", params = params, id = 1).dumps()
            request = hipc.Request(resource = "event", body = body.encode("utf-8")).bytes()
            self.sock.send(request)

    def color_changed(self, button):
        if self.sock:
            color = self.color_entry.get_text()
            body = jsonrpc.Request(jsonrpc = "2.0", method="report_event", params = {"name": "device_status_changed", "data": {"id": self.did, "status": {"color": color}}}, id = 1).dumps()
            request = hipc.Request(resource = "event", body = body.encode("utf-8")).bytes()
            self.sock.send(request)

    def brightness_changed(self, button):
        if self.sock:
            brightness = self.brightness_entry.get_text()
            body = jsonrpc.Request(jsonrpc = "2.0", method="report_event", params = {"name": "device_status_changed", "data": {"id": self.did, "status": {"brightness": brightness}}}, id = 1).dumps()
            request = hipc.Request(resource = "event", body = body.encode("utf-8")).bytes()
            self.sock.send(request)

    def select(self):
        while True:
            if self.stop:
                break
            else:
                events = self.sel.select(0.01)
                if events:
                    for key, mask in events:
                        if key.fileobj == self.sock:
                            self.read()

    def read(self):
        data = self.sock.recv(1000)
        #print(data)
        if data:
            self.parser.parse(data)
        else:
            self.sel.unregister(self.sock)
            self.sock.close()
            self.btn_connect.set_sensitive(True)
            self.btn_disconnect.set_sensitive(False)

    def handle_message(self, message):
        if isinstance(message, hipc.Request):
            request = jsonrpc.Request.loads(message.body.decode("utf-8"))
            dest = message.headers.get("origin")
            if request.method == "power_on":
                self.power_switch.set_active(True)
                body = jsonrpc.Response(jsonrpc="2.0", result = None, id = request.id).dumps()
                resp = hipc.Response(dest = dest, body = body.encode("utf-8")).bytes()
                self.sock.send(resp)

            elif request.method == "power_off":
                self.power_switch.set_active(False)
                body = jsonrpc.Response(jsonrpc="2.0", result = None, id = request.id).dumps()
                resp = hipc.Response(dest = dest, body = body.encode("utf-8")).bytes()
                self.sock.send(resp)

            elif request.method == "get_power_state":
                body = jsonrpc.Response(jsonrpc="2.0", result = self.power_switch.get_active(), id = request.id).dumps()
                resp = hipc.Response(dest = dest, body = body.encode("utf-8")).bytes()
                self.sock.send(resp)

            elif request.method == "get_color":
                color = self.color_entry.get_text()
                body = jsonrpc.Response(jsonrpc="2.0", result = int(color, 16), id = request.id).dumps()
                resp = hipc.Response(dest = dest, body = body.encode("utf-8")).bytes()
                self.sock.send(resp)

            elif request.method == "set_color":
                color = request.params
                self.color_entry.set_text(str(color))
                body = jsonrpc.Response(jsonrpc="2.0", result = None, id = request.id).dumps()
                resp = hipc.Response(dest = dest, body = body.encode("utf-8")).bytes()
                self.sock.send(resp)

            elif request.method == "get_brightness":
                brightness = self.brightness_entry.get_text()
                body = jsonrpc.Response(jsonrpc="2.0", result = int(brightness), id = request.id).dumps()
                resp = hipc.Response(dest = dest, body = body.encode("utf-8")).bytes()
                self.sock.send(resp)

            elif request.method == "set_brightness":
                brightness = request.params
                self.brightness_entry.set_text(str(brightness))
                body = jsonrpc.Response(jsonrpc="2.0", result = None, id = request.id).dumps()
                resp = hipc.Response(dest = dest, body = body.encode("utf-8")).bytes()
                self.sock.send(resp)

        elif isinstance(message, hipc.Response):
            response = jsonrpc.Response.loads(message.body.decode("utf-8"))
            if response.id == 10000:
                self.did = int(response.result)

    def connect_server(self, button):
        type = self.sock_type.get_active()
        if type == 0:
            addr = self.sock_addr.get_text()
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
            self.sock.connect(addr)
        elif type == 1:
            addr = self.sock_addr.get_text()
            port = self.sock_port.get_text()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.sock.connect((addr, int(port)))

        button.set_sensitive(False)
        self.btn_disconnect.set_sensitive(True)

        self.sel.register(self.sock, selectors.EVENT_READ, self.read)

        self.add_device()

    def disconnect_server(self, button):
        self.sel.unregister(self.sock)
        self.sock.close()
        button.set_sensitive(False)
        self.btn_connect.set_sensitive(True)

    def add_device(self):
        device = {
            "uniqid": self.uniqid_entry.get_text(),
            "vender": self.vender_entry.get_text(),
            "hwversion": self.hwversion_entry.get_text(),
            "swversion": self.swversion_entry.get_text(),
            "type": "lighting",
            "operations": ["power_on", "power_off", "get_power_state", "set_color", "get_color", "set_brightness", "get_brightness"],
            "status": {
                "power": "on" if self.power_switch.get_active() else "off",
                "color": self.color_entry.get_text() if self.color_entry.get_text() else 0x0,
                "brightness": int(self.brightness_entry.get_text()) if self.brightness_entry.get_text() else 0
            }
        }

        body = jsonrpc.Request(jsonrpc = "2.0", method = "add_device", params = device, id = 10000).dumps()
        request = hipc.Request(resource = "device", body = body.encode("utf-8")).bytes()
        self.sock.send(request)

    def run(self):
        self.sock_type.set_active(0)
        self.sock_addr.set_text("/tmp/hub_sock")
        self.btn_disconnect.set_sensitive(False)
        thread = threading.Thread(target=self.select)
        thread.start()
        self.window.show_all()
        self.port_box.hide()
        Gtk.main()

    def exit(self, window, event):
        self.stop = True
        Gtk.main_quit()
        sys.exit()

if __name__ == "__main__":
    client = LightingClient()
    client.run()
