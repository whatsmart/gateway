#!/usr/bin/env python3

import sqlite3
import hashlib
import random
import traceback
import json

def catch_db_error(func):
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except Exception as e:
            print("sqlite3:", e)
            traceback.print_exc()
        else:
            return ret

    return wrapper

class User(object):
    """用户具有如下属性:
    id 用户id
    gid 用户组id
    username 用户名
    password 用的密码
    token 用户标识
    """

    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)

    @catch_db_error
    def get_user_from_token(self, token):
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        sql = 'select * from user where token = ' + '"' + token + '"'
        cursor.execute(sql)
        result = cursor.fetchone()
        user = {}
        if result:
            for key in result.keys():
                user[key] = result[key]
        cursor.close()
        return user

    @catch_db_error
    def create_user(self, username, password):
        cursor = self.conn.cursor()
        m = hashlib.md5()
        m.update(password.encode("utf-8"))
        digest = m.digest()
        cursor.execute('''SELECT * FROM user''')
        users = cursor.fetchall()

        try:
            cursor.execute('''INSERT INTO user (username, password, `group`) VALUES (?, ?, ?)''', (username, digest, "user" if len(users) else "admin"))
        except Exception:
            #用户名已经存在
            cursor.close()
            return False
        else:
            self.conn.commit()
            uid = cursor.lastrowid
            cursor.close()
            return self.get_user(uid)

    @catch_db_error
    def delete_user(self, uid):
        #print(type(uid))
        cursor = self.conn.cursor()
        cursor.execute('''DELETE FROM user WHERE id = ?''', str(uid))
        num = cursor.rowcount
        self.conn.commit()
        cursor.close()
        if num != 1:
            return False
        return True

    @catch_db_error
    def update_password(self, uid, password):
        cursor = self.conn.cursor()

        m = hashlib.md5()
        m.update(password.encode("utf-8"))
        digest = m.digest()

        cursor.execute('''UPDATE user SET password = ? WHERE id = ?''', (digest, str(uid)))
        num = cursor.rowcount
        self.conn.commit()
        cursor.close()
        if num == 0:
            return False
        return True

    def gen_token(self, length):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        r = len(chars) - 1
        token = ""
        for i in range(length):
            token += chars[random.randint(0, r)]
        return token

    @catch_db_error
    def login_user(self, username, password):
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        sql = 'SELECT id, username, password, `group`, permission FROM user WHERE username = ' + '"' + username + '"'
        cursor.execute(sql)
        #print(cursor.rowcount)
        user = cursor.fetchone()
        m = hashlib.md5()
        m.update(password.encode("utf-8"))
        digest = m.digest()
        if user["password"] == digest:
            token = self.gen_token(40)
            cursor.execute('''update user set token = ? where username = ?''', (token, username))
            self.conn.commit()
            cursor.close()
            return {"id": user["id"], "group": user["group"], "permission": json.loads(user["permission"]) if user["permission"] else [], "token": token}
        cursor.close()
        return False

    @catch_db_error
    def logout_user(self, uid):
        cursor = self.conn.cursor()
        cursor.execute('update user set token = "" where id = ?', str(uid))
        num = cursor.rowcount
        cursor.close()
        self.conn.commit()
        if num == 0:
            return False
        return True

    @catch_db_error
    def get_users(self):
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute('''SELECT id, username, `group`, permission FROM user''')
        result = cursor.fetchall()

        ret = []
        for u in result:
            user = {
                "id": u["id"],
                "username": u["username"],
                "group": u["group"],
                "permission": json.loads(u["permission"]) if u["permission"] else []
            }
            ret.append(user)

        cursor.close()
        return ret

    @catch_db_error
    def get_user(self, uid):
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute('''SELECT id, username, `group`, permission FROM user where id = ?''', str(uid))
        result = cursor.fetchone()

        if result:
            ret = {
                "id": result["id"],
                "username": result["username"],
                "group": result["group"],
                "permission": json.loads(result["permission"]) if result["permission"] else []
            }

            cursor.close()
            return ret
        else:
            cursor.close()
            return False

    @catch_db_error
    def set_permission(self, uid, perm):
        perm = json.dumps(perm)
        cursor = self.conn.cursor()
        sql = 'update user set permission = ' + '\'' + perm + '\' ' + 'where id = ' + str(uid)
        cursor.execute(sql)
        num = cursor.rowcount
        cursor.close()
        self.conn.commit()
        if num == 0:
            return False
        return True
