#!/usr/bin/env python3

import sqlite3
import os

dbpath = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "gateway/data/gateway.db")

conn = sqlite3.connect(dbpath)
cursor = conn.cursor()

cursor.execute('create table user (id ITEGER  PRIMARY KEY, username text UNIQUE, password blob, `group` text,  permission text, token text)');
cursor.execute('create table device (id integer primary key, uniqid text unique, name text, position text)')
cursor.execute('create table client (id integer primary key, username text, deviceid text unique, devicename text, platform text);')

cursor.close()
conn.close()
