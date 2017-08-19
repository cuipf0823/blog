# !/usr/bin/python
# coding=utf-8

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_pagedown import PageDown
from config import config
import redis


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
pagedown = PageDown()

rd = None


login_manager = LoginManager()
# 防止会话被篡改，设置为strong，会记录客户端的IP和浏览器的用户代理信息
login_manager.session_protection = 'strong'
# 设置登录页面的端点
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 初始化
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    global rd
    rd = redis.Redis(host=config[config_name].REDIS_IP, port=config[config_name].REDIS_PORT,
                     db=config[config_name].REDIS_DB, password=config[config_name].REDIS_PWD)
    login_manager.init_app(app)

    # 注册蓝图
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    # url_prefix为可选参数，如果设置，注册后的蓝本中定义的所有路由都会加上指定的前缀
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app
