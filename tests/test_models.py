# !/usr/bin/python
# coding=utf-8

import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User('cat')

    def tearDown(self):
        self.user = None

    def test_password_verification(self):
        self.assertTrue(self.user.verify_password('cat'))
        self.assertFalse(self.user.verify_password('dog'))

    def test_password_hash_are_rand(self):
        u1 = User('test')
        u2 = User('test')
        self.assertTrue(u1.password != u2.password)


# 构造测试集合
def suite():
    suite = unittest.TestSuite()
    suite.addTest(UserModelTestCase('test_password_hash_are_rand'))
    suite.addTest(UserModelTestCase('test_password_verification'))