# !/usr/bin/python
# coding=utf-8
from flask import render_template
from flask import redirect, url_for, flash, abort
from flask_login import login_required
from flask_login import current_user
from . import main
from ..models import get_user_by_name, update_frofile, update_admin_profile
from ..models import get_user_by_id, Post, Permission
from ..data import db_posts
from .forms import EditProfileForm, EditProfileFormAdmin, PostForm
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(form.title.data, current_user.username, form.body.data, '')
        db_posts.publish_post(post.title, post.author, post.content, post.category)
        return redirect(url_for('.index'))
    posts = db_posts.posts_by_page(1)
    return render_template('index.html', form=form, posts=posts, permission=Permission)


@main.route('/user/<username>')
def user(username):
    user_info = get_user_by_name(username)
    if user_info is None:
        abort(404)
    return render_template('user.html', user=user_info)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        # 更新数据库
        update_frofile(current_user.id, current_user.username, current_user.location, current_user.about_me)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.username
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    edit_user = get_user_by_id(user_id)
    form = EditProfileFormAdmin(user=edit_user)
    if form.validate_on_submit():
        edit_user.username = form.username.data
        edit_user.email = form.email.data
        edit_user.confirmed = (1 if form.confirmed.data else 0)
        edit_user.location = form.location.data
        edit_user.about_me = form.about_me.data
        edit_user.role_id = form.role.data
        update_admin_profile(user_id, edit_user)
        flash('The profile has been updated !')
        return redirect(url_for('.user', username=edit_user.username))
    form.username.data = edit_user.username
    form.email.data = edit_user.email
    form.confirmed.data = edit_user.confirmed
    form.role.data = edit_user.role_id
    form.location.data = edit_user.location
    form.about_me.data = edit_user.about_me
    return render_template('edit_profile.html', form=form, user=edit_user)
