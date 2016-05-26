#!/usr/bin/env python3

"""payload是字典格式,如下：
notification用于通知消息的展示，message是透传给用户的信息。
payload中的字段信息参考谷歌gcm：https://developers.google.com/cloud-messaging/http-server-ref

{
    "targets": [
        ["deviceid", "platform"],
        ...
    ], #由具体推送程序填写
    "options": {
        "expired": 3600,
    }
    "notification": {
        "title": "notification title",
        "body": "notification content",
        "icon": "filename",
        ... 后续添加
    }
    "data": {
        "device_state_changed": {
            "id": 123
        }
    }
}
"""

class Push(object):
    def __init__(self):
        pass

    def push_to_all(self, payload):
        raise NotImplementedError

    def push_to_all_except(self, payload, users = None, devices = None):
        raise NotImplementedError

    def push_to_user(self, payload, username):
        raise NotImplementedError

    def push_to_device(self, payload, deviceid):
        raise NotImplementedError
