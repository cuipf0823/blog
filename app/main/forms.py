# !/usr/bin/python
# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import Regexp
from ..models import Role
from ..models import is_email_register
from ..models import is_name_register


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 128)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileFormAdmin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 128), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                         'Username must hava only '
                                                                                         'letters, numbers, '
                                                                                         'dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 128)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileFormAdmin, self).__init__(*args, **kwargs)
        self.role.choices = [(key, Role.roles[key][2]) for key in Role.roles.keys()]
        self.user = user

    # 表单函数中定义了validate_开头的函数并且后面紧跟字段名的方法，这些方法
    # 会和常规的验证函数一起调用
    def validate_email(self, field):
        if field.data != self.user.email and is_email_register(field.data):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and is_name_register(field.data):
            raise ValidationError('Username already registered.')


class PostForm(FlaskForm):
    title = StringField('Title: ')
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')





















