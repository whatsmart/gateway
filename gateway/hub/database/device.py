#!/usr/bin/env python3

import sqlite3

class Device(object):
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)

    def add_device(self, uniqid):
        cursor = self.conn.cursor()
        sql = 'select id from device where uniqid = "' + uniqid + '"'
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            return result[0]
        sql = 'insert into device (uniqid) values ("' + uniqid + '")'
        cursor.execute(sql)
        did = cursor.lastrowid
        self.conn.commit()
        cursor.close()
        self.conn.close()
        return did
