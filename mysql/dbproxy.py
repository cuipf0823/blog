# !/usr/bin/python
# coding=utf-8
from app import db


class DBUserProxy:

    def __init__(self):
        self.__con = db
        self.__table_name = 'blog_users'

    # 先不考虑db的关闭
    def __del__(self):
        pass

    def get_user(self, email):
        """
        获取玩家根据email
        """
        cursor = self.__con.cursor()
        sqlstr = "SELECT id, user_name, pwd_hash, role_id FROM %s WHERE email = '%s' " % (self.__table_name, email)
        cursor.execute(sqlstr)
        ret = cursor.fetchone()
        cursor.close()
        return ret

    def get_user_by_id(self, user_id):
        cursor = self.__con.cursor()
        sqlstr = "SELECT user_name, pwd_hash, email, role_id FROM %s WHERE id = %d " % (self.__table_name, user_id)
        cursor.execute(sqlstr)
        ret = cursor.fetchone()
        cursor.close()
        return ret

    def is_register(self, email):
        """
        判断邮件地址是否注册过
        """
        cur = self.__con.cursor()
        sqlstr = "SELECT * FROM %s WHERE email = '%s' " % (self.__table_name, email)
        cur.execute(sqlstr)
        ret = cur.fetchall()
        cur.close()
        return len(ret)

    def is_user_register(self, username):
        """
        判断用户名字是否注册过
        """
        cur = self.__con.cursor()
        sqlstr = "SELECT * FROM %s WHERE user_name = '%s' " % (self.__table_name, username)
        cur.execute(sqlstr)
        ret = cur.fetchall()
        cur.close()
        return len(ret)

    def add_user(self, username, pwd, email, role_id):
        """
        添加新用户  传递hash 之后的pwd 返回用户ID值
        """
        cur = self.__con.cursor()
        sqlstr = "INSERT into %s (user_name, pwd_hash, email, role_id, reg_time) VALUES " \
                 "('%s', '%s', '%s', %u, NOW())" % (self.__table_name, username, pwd, email, role_id)
        ret = cur.execute(sqlstr)
        self.__con.commit()
        if ret != 1:
            return 0
        sqlstr = "select last_insert_id() FROM %s" % self.__table_name
        cur.execute(sqlstr)
        ret = cur.fetchall()[0]
        cur.close()
        return ret

    def update_pwd(self, user_id, pwd):
        """
         修改用户的pwd 传递是hash之后的pwd
        """
        cur = self.__con.cursor()
        sqlstr = "UPDATE %s SET pwd_hash = '%s' WHERE id = %d" % (self.__table_name, pwd, user_id)
        ret = cur.execute(sqlstr)
        cur.close()
        return ret



