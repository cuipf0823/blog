# !/usr/bin/python
# coding=utf-8

from flask import Blueprint


# 实例化Blueprint类对象创建蓝本
main = Blueprint('main', __name__)

from . import views
from . import errors



