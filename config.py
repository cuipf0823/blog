# !/usr/bin/python
# coding=utf-8
import os

# 存储配置
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = 'smtp.163.com'  # 电子邮件服务器的主机名或IP地址
    MAIL_PORT = '25'  # 电子邮件服务器的端口
    MAIL_USE_TLS = True  # 启用传输层安全
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # 邮件账户用户名
    MAIL_PASSWORD = os.environ.get('MAIL_PWD')  # 邮件账户的密码
    MAIL_SUBJECT_PREFIX = os.environ.get('MAIL_SUBJECT_PREFIX')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN')

    def __init__(self):
        pass

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    REDIS_IP = os.environ.get('REDIS_DEV_IP')
    REDIS_PORT = os.environ.get('REDIS_DEV_PORT')
    REDIS_DB = int(os.environ.get('REDIS_DEV_DB'))
    REDIS_PWD = os.environ.get('REDIS_DEV_PWD')


class TestConfig(Config):
    TESTING = True
    REDIS_IP = os.environ.get('REDIS_TEST_IP')
    REDIS_PORT = os.environ.get('REDIS_TEST_PORT')
    REDIS_DB = os.environ.get('REDIS_TEST_DB')
    REDIS_PWD = os.environ.get('REDIS_TEST_PWD')

config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}

