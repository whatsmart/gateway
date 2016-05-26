#!/usr/bin/env python3

import sqlite3

class Client(object):
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)

    def get_client_by_deviceid(self, deviceid):
        assert deviceid
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        sql = 'select * from client where deviceid = "' + deviceid + '"'
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            client = {
                "id": result["id"],
                "username": result["username"],
                "deviceid": result["deviceid"],
                "devicename": result["devicename"],
                "platform": result["platform"]
            }
            cursor.close()
            return client
        else:
            cursor.close()
            return None

    def get_clients_by_username(self, username):
        assert username
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        sql = 'select * from client where username = "' + username + '"'
        cursor.execute(sql)

        result = cursor.fetchall()
        if result:
            clients = []
            for row in result:
                client = {
                    "id": row["id"],
                    "username": row["username"],
                    "deviceid": row["deviceid"],
                    "devicename": row["devicename"],
                    "platform": row["platform"]
                }
                clients.append(client)
            cursor.close()
            return clients
        else:
            cursor.close()
            return None

    def get_clients(self):
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute('select * from client')
        result = cursor.fetchall()
        if result:
            clients = []
            for row in result:
                client = {
                    "id": row["id"],
                    "username": row["username"],
                    "deviceid": row["deviceid"],
                    "devicename": row["devicename"],
                    "platform": row["platform"]
                }
                clients.append(client)

            cursor.close()
            return clients
        else:
            cursor.close()
            return None

    def set_client_info(self, deviceid, name, platform):
        cursor = self.conn.cursor()
        sql = 'insert into client (deviceid, devicename, platform) values (' + '"' + deviceid + '", "' + name + '", "' + platform + '"' + ')'
        try:
            cursor.execute(sql)
        except sqlite3.IntegrityError:
            pass
        if cursor.rowcount != 1:
            sql = 'update client set devicename = ' + '"' + name + '", ' + 'platform = ' + '"' + platform + '" where deviceid = ' + '"' + deviceid + '"'
            cursor.execute(sql)
            if cursor.rowcount != 1:
                cursor.close()
                return False
            else:
                cursor.close()
                self.conn.commit()
                return True
        else:
            cursor.close()
            self.conn.commit()
            return True

    def bind_user(self, deviceid, username):
        cursor = self.conn.cursor()
        sql = 'update client set username = ' + '"' + username + '" where deviceid = ' + '"' + deviceid + '"'
        cursor.execute(sql)
        if cursor.rowcount != 1:
            cursor.close()
            return False
        else:
            cursor.close()
            self.conn.commit()
            return True

    def unbind_user(self, deviceid, username):
        cursor = self.conn.cursor()
        sql = 'update client set username = "" where deviceid = ' + '"' + deviceid + '"'
        cursor.execute(sql)
        if cursor.rowcount != 1:
            cursor.close()
            return False
        else:
            cursor.close()
            self.conn.commit()
            return True

    def __del__(self):
        self.conn.close()
