# !/usr/bin/python
# coding=utf-8
from datetime import datetime
from .. import rd
from .. import util

'''
1. 用户详细信息; 使用redis中的散列类型保存, key是'user:id';
2. 用户总数; 保存于users:count中;
3. email.to.id 根据email查询到具体用户ID; 这里可以调整为
4. name.to.id 根据用户名查询到具体用户ID
'''


def reg_user(username, pwd, email, role_id):
    """
    add new user pwd: hash pwd
    """
    user_id = rd.incr('users:count')
    # 保存用户信息
    rd.hmset('user:%d' % user_id, {'name': username, 'password': pwd, 'email': email, 'role_id': role_id,
                                   'member_since': datetime.utcnow(), 'confirmed': 0, 'about_me': '', 'location': '',
                                   'last_seen': datetime.utcnow()})
    rd.hset('email.to.id', email, user_id)
    rd.hset('name.to.id', username, user_id)
    return user_id


def get_user(email):
    """
    get user infomation by user email
    """
    user_id = rd.hget('email.to.id', email)
    if user_id is not None:
        return get_user_by_id(user_id.decode("utf-8"))


def get_user_by_name(name):
    """
    get user infomation by user name
    """
    user_id = rd.hget('name.to.id', name)
    if user_id is not None:
        return get_user_by_id(user_id.decode("utf-8"))


def get_user_by_id(user_id):
    """
    get user infomation by user id
    """
    user_info = util.convert(rd.hgetall('user:{}'.format(user_id)))
    if len(user_info) != 0:
        user_info['user_id'] = int(user_id)
        return user_info


def change_password(user_id, pwd):
    return rd.hset('user:%d' % user_id, 'password', pwd)


def is_email_reg(email):
    return rd.hexists('email.to.id', email)


def is_username_reg(name):
    return rd.hexists('name.to.id', name)


def confirm(user_id):
    return rd.hset('user:%d' % user_id, 'confirmed', 1)


def update_last_seen(user_id, utctime):
    return rd.hset('user:%d' % user_id, 'last_seen', utctime)


def update_profile(user_id, username, location, about_me):
    return rd.hmset('user:%d' % user_id, {'name': username, 'location': location, 'about_me': about_me})


def update_admin_profile(user_id, user):
    return rd.hmset('user:%d' % user_id, {'name': user.username, 'email': user.email, 'confirmed': user.confirmed,
                                          'role_id': user.role_id, 'location': user.location, 'about_me': user.about_me})
