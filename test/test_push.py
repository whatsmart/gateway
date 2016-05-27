#!/usr/bin/env python3

from gateway.base import pushman
from tornado.ioloop import IOLoop

payload = {
    "expired": 3600,
    "notification": {
        "title": "notification title",
        "body": "notification content"
    },
    "data": {
        "device_state_changed": {
            "id": 123
        }
    }
}

push = pushman.PushMan("http://localhost:8800")

def send_to_user():
    return push.push_to_user(payload, "安迪")

def send_to_device():
    return push.push_to_device(payload, "9d0b7888fc0efd9c39646b4f44b73f997a782a240aaa9df6ec7904bb76aeb20a")

def send_to_all():
    return push.push_to_all(payload)

def send_to_all_except_users():
    return push.push_to_all_except_users(payload, ["test"])

def send_to_all_except_devices():
    return push.push_to_all_except_devices(payload, ["1cf08127b35cdd89389a90e6617b0695"])

loop = IOLoop.instance()
loop.run_sync(send_to_all)
