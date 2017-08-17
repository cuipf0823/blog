# !/usr/bin/python
# coding=utf-8

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import Regexp, EqualTo
from ..models import is_email_register
from ..models import is_name_register


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    rem_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                         'Username must hava only '
                                                                                         'letters, numbers, '
                                                                                         'dots or underscores')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Password must'
                                                                                                  ' mathch.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    # 表单函数中定义了validate_开头的函数并且后面紧跟字段名的方法，这些方法
    # 会和常规的验证函数一起调用
    def validate_email(self, field):
        if is_email_register(field.data):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if is_name_register(field.data):
            raise ValidationError('Username already registered.')


class ChangePwdForm(FlaskForm):
    old_pwd = PasswordField('Old password', validators=[DataRequired()])
    pwd = PasswordField('New password', validators=[DataRequired(), EqualTo('pwd2', message='Passwords must match')])
    pwd2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    pwd = PasswordField('New password', validators=[DataRequired(), EqualTo('pwd2', message='Passwords must match')])
    pwd2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if not is_email_register(field.data):
            raise ValidationError('Unknown email address')







