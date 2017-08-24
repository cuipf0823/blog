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

"""
1. 用户关注者使用列表类型保存， 键值为：user:follower:user_id
2. 用户关注的人列表，同样也是用列表类型保存， 键值为：user:following:user_id
"""

USER_FOLLOWER_LIST = 'user:follower:'
USER_FOLLOWING_LIST = 'user:following:'


def follow(user_id, follower):
    """
     user_id following follower
    """
    rd.lpush(USER_FOLLOWING_LIST + '{}'.format(user_id), follower)
    rd.lpush(USER_FOLLOWER_LIST + '{}'.format(follower), user_id)


def unfollow(user_id, follower):
    """
     user_id cancel follow followers
    """
    rd.lrem(USER_FOLLOWING_LIST + '{}'.format(user_id), follower)
    rd.lrem(USER_FOLLOWER_LIST + '{}'.format(follower), user_id)


def is_followed(user_id, follower):
    """
     whether user_id has followed followers
     效率可能较低但暂未想到好的方法
    """
    followings = rd.lrange(USER_FOLLOWING_LIST + '{}'.format(user_id), 1, -1)
    if '{}'.format(follower).encode() in followings:
        return True
    else:
        return False


def is_followed_by(user_id, follower):
    """
     whether user_is has been followed by follower
    """
    followers = rd.lrange(USER_FOLLOWER_LIST + '{}'.format(user_id), 1, -1)
    if '{}'.format(follower).encode() in followers:
        return True
    else:
        return False


def followers_by_page(user_id, page_id, per_page):
    """
    paging display
    get followers list by user_id
    """
    pages = int(rd.llen(USER_FOLLOWER_LIST + '{}'.format(user_id)) / per_page + 1)
    if 0 < page_id <= pages:
        return util.convert(rd.lrange(USER_FOLLOWER_LIST + '{}'.format(user_id), (page_id - 1) * per_page,
                                      page_id * per_page - 1))
    print('followers_by_page invaild param user_id {0} page id[{1}, {2}]: {3}'.format(user_id, 1, pages, page_id))


def following_by_page(user_id, page_id, per_page):
    """
    paging display
    get has been following user list by user_id
    """
    pages = int(rd.llen(USER_FOLLOWING_LIST + '{}'.format(user_id)) / per_page + 1)
    if 0 < page_id <= pages:
        return util.convert(rd.lrange(USER_FOLLOWING_LIST + '{}'.format(user_id), (page_id - 1) * per_page,
                                      page_id * per_page - 1))
    print('following_by_page invaild param user_id {0} page id[{1}, {2}]: {3}'.format(user_id, 1, pages, page_id))