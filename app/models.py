# !/usr/bin/python
# coding=utf-8
from datetime import datetime
from flask import current_app, request
from flask_login import AnonymousUserMixin
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from .data import db_users, db_posts
from . import login_manager
import hashlib
import math

# maximum number articles per page
POST_NUM_PAGE = 10

ANONYMOUS_ROLE = 0  # 匿名用户 为登陆的用户, 只有阅读权限
USER_ROLE = 1  # 普通用户  新用户默认角色, 可以发表文章, 评论, 关注他人
MODERATOR_ROLE = 2  # 协管员 相比普通用户 增加审查不当平路的权限
ADMIN_ROLE = 3  # 管理员 全部权限 包括修改其他用户角色的权限


class Permission:
    FOLLOW = 0x01  # 关注其他用户
    COMMENT = 0x02  # 在他人文章下面发布评论
    WRITE_ARTICLES = 0x04  # 写文章
    MANAGER_COMMENTS = 0x08  # 查看他人发表的评论
    ADMINISTER = 0x80  # 管理网站

    def __init__(self):
        pass


class Role:
    """
    用户角色
    """
    roles = {
        USER_ROLE: (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True, 'User'),
        MODERATOR_ROLE: (Permission.FOLLOW |
                         Permission.COMMENT |
                         Permission.WRITE_ARTICLES |
                         Permission.MANAGER_COMMENTS, False, 'Moderator'),
        ADMIN_ROLE: (0xff, False, 'Administrator')
        }

    def __init__(self):
        pass

    @classmethod
    def permissions(cls, role_id):
        if role_id in cls.roles.keys():
            return cls.roles[role_id][0]
        return 0


# 处于一致性考虑，对象继承于AnonymousUserMixin类，并将其设为用户登录时current_user的值
# 目的是：这样用户不用检查是否登录，就可以自由调用current_user.can()和current_user.is_administrator()
class AnonymousUser(AnonymousUserMixin):

    @staticmethod
    def can(permissions):
        return False

    @staticmethod
    def is_administrator():
        return False


class User(UserMixin):
    def __init__(self, dicts):
        self._id = dicts['user_id']
        self._username = dicts['name']
        self._password_hash = dicts['password']
        self._email = dicts['email']
        self._role_id = int(dicts['role_id'])
        self._confirmed = dicts['confirmed']
        self._location = dicts['location']
        self._about_me = dicts['about_me']
        # datetime.strptime('2017-02-14 09:20:54.666000', '%Y-%m-%d %H:%M:%S.%f')
        self._member_since = None
        if dicts['member_since'] is not None:
            self._member_since = datetime.strptime(dicts['member_since'], '%Y-%m-%d %H:%M:%S.%f')
        self._last_seen = None
        if dicts['last_seen'] is not None:
            self._last_seen = datetime.strptime(dicts['last_seen'], '%Y-%m-%d %H:%M:%S.%f')

    def verify_password(self, pwd):
        return check_password_hash(self._password_hash, pwd)

    def generate_confirmation_token(self, expiration=3600):
        """
        产生用户确认令牌
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self._id})

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self._id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception as e:
            print(e)
            return False
        if data.get('confirm') != self._id:
            return False
        self._confirmed = True
        db_users.confirm(self._id)
        return True

    def reset_pwd(self, token, new_pwd):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception as e:
            print(e)
            return False
        if data.get('reset') != self._id:
            return False
        self._password_hash = new_pwd
        return True

    def can(self, permissions):
        return permissions & Role.permissions(self._role_id) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        utctime = datetime.utcnow()
        self._last_seen = utctime
        db_users.update_last_seen(self._id, utctime)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        vhash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=vhash, size=size, default=default, rating=rating)

    @property
    def confirmed(self):
        return self._confirmed

    @confirmed.setter
    def confirmed(self, value):
        self._confirmed = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value):
        self._password_hash = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def role_id(self):
        return self._role_id

    @role_id.setter
    def role_id(self, value):
        self._role_id = value

    @property
    def about_me(self):
        return self._about_me

    @about_me.setter
    def about_me(self, value):
        self._about_me = value

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def member_since(self):
        return self._member_since

    @member_since.setter
    def member_since(self, value):
        self._member_since = value

    @property
    def last_seen(self):
        return self._last_seen

    @last_seen.setter
    def last_seen(self, value):
        self._last_seen = value

    def __str__(self):
        return ''


def get_user(email):
    user_info = db_users.get_user(email)
    if user_info is not None:
        return User(user_info)
    return user_info


def get_user_by_id(user_id):
    user_info = db_users.get_user_by_id(user_id)
    if user_info is not None:
        return User(user_info)
    return user_info


def get_user_by_name(name):
    user_info = db_users.get_user_by_name(name)
    if user_info is not None:
        return User(user_info)
    return user_info


def register_user(name, pwd, email):
    if email == current_app.config['MAIL_ADMIN']:
        return db_users.reg_user(name, generate_password_hash(pwd), email, ADMIN_ROLE)
    else:
        return db_users.reg_user(name, generate_password_hash(pwd), email, USER_ROLE)


def change_password(user_id, pwd):
    return db_users.change_password(user_id, generate_password_hash(pwd))


def is_email_register(email):
    return db_users.is_email_reg(email)


def is_name_register(username):
    return db_users.is_username_reg(username)


def update_frofile(user_id, user_name, location, about_me):
    return db_users.update_profile(user_id, user_name, location, about_me)


def update_admin_profile(user_id, user):
    return db_users.update_admin_profile(user_id, user)

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """
    回调函数，根据用户ID查找用户
    """
    print('user %s login successful' % user_id)
    return get_user_by_id(int(user_id))


class Post:
    def __init__(self, dicts):
        self._title = dicts['title']
        self._author_id = dicts['author_id']
        self._content = dicts['content']
        self._category = dicts['category']
        self._time = dicts['time']
        self._author = get_user_by_id(self.author_id).username

    def __str__(self):
        return ''

    @property
    def title(self):
        return self._title

    @property
    def author_id(self):
        return self._author_id

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def time(self):
        return self._time

    def author_gravatar(self, size=100, default='identicon', rating='g'):
        user = get_user_by_id(self.author_id)
        return user.gravatar(size, default, rating)


def publish_post(title, author_id, content, category):
    db_posts.publish_post(title, author_id, content, category)


def posts_by_page(page_id):
    post_ids = db_posts.posts_by_page(page_id, POST_NUM_PAGE)
    if post_ids is not None:
        posts = []
        for post_id in post_ids:
            posts.append(Post(db_posts.get_post(post_id)))
        return posts


def posts_by_author(author_id, page_id):
    post_ids = db_posts.posts_by_author(author_id, page_id, POST_NUM_PAGE)
    if post_ids is not None:
        posts = []
        for post_id in post_ids:
            posts.append(Post(db_posts.get_post(post_id)))
        return posts


def total_posts():
    return db_posts.total_posts()


class Pagination:
    def __init__(self, page, items, total, per_page=POST_NUM_PAGE):
        # the current page number
        self._page = page
        # the number of items to be displayed on a page
        self._per_page = per_page
        # the total number
        self._total = total
        # the items for the current page
        self._items = items
        # the total number of pages
        if self._per_page == 0:
            self._pages = 0
        else:
            self._pages = int(math.ceil(self._total / float(self._per_page)))

    @property
    def page(self):
        return self._page

    @property
    def pages(self):
        return self._pages

    @property
    def total(self):
        return self._total

    @property
    def items(self):
        return self._items

    @property
    def pre_page(self):
        return self._per_page

    @property
    def has_prev(self):
        """
         return True if a previous page exists
        """
        return self._page > 1

    @property
    def has_next(self):
        """
         return True if a next page exists
        """
        return self._pages > self._page

    @property
    def pre_num(self):
        """
         number of the previous page.
        """
        if self.has_prev:
            return self._page - 1

    @property
    def next_num(self):
        """
         number of the next page
        """
        if self.has_next:
            return self._page + 1

    def next(self):
        """
        return a class Ragination
        """
        assert self.has_next, 'must be has next'
        return Pagination(self.next_num, posts_by_page(self.next_num), self.total)

    def prev(self):
        """
        return a class Ragination
        """
        assert self.has_prev, 'must be has prev'
        return Pagination(self.pre_num, posts_by_page(self.pre_num), self.total)

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (self._page - left_current - 1 < num < self._page + right_current) or \
                    (num > self._pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num
        



