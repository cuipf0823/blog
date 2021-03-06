# !/usr/bin/python
# coding=utf-8
from flask import render_template, request
from flask import redirect, url_for, flash, abort
from flask_login import login_required
from flask_login import current_user
from . import main
from ..models import get_user_by_name, update_frofile, update_admin_profile
from ..models import get_user_by_id, Permission, Pagination
from ..models import publish_post, posts_by_page, posts_by_author
from ..models import total_posts, total_posts_by_author, get_post
from ..models import update_post_content, Relation, FOLLOWERS_NUM_PAGE
from .forms import EditProfileForm, EditProfileFormAdmin, PostForm
from ..decorators import admin_required, permission_required
import html2text


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        publish_post(form.title.data, current_user.id, form.body.data, '')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    posts = posts_by_page(page)
    pagination = Pagination(page, posts, total_posts())
    return render_template('index.html', form=form, posts=posts, permission=Permission, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user_info = get_user_by_name(username)
    if user_info is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    posts = posts_by_author(user_info.id, page)
    pagination = Pagination(page, posts, total_posts_by_author(user_info.id))
    return render_template('user.html', user=user_info, posts=posts, pagination=pagination,
                           permission=Permission, relation=Relation)


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


@main.route('/post/<int:post_id>')
def post(post_id):
    post_info = get_post(post_id)
    return render_template('post.html', posts=[post_info])


@main.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post_info = get_post(post_id)
    # 管理员权限可以修改其他人的
    if current_user.id != post_info.author_id and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        # 更新post 内容
        update_post_content(post_id, form.body.data)
        flash('The post has been updated.')
        return redirect(url_for('.post', post_id=post_id))
    form.body.data = html2text.html2text(post_info.content)
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user_info = get_user_by_name(username)
    if user_info is None:
        flash('Invalid user!')
        return redirect(url_for('.index'))
    if Relation.is_followed(current_user.id, user_info.id):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username, relation=Relation()))
    Relation.follow(current_user.id, user_info.id)
    flash('You are now following {}.'.format(username))
    return redirect(url_for('.user', username=username, relation=Relation()))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user_info = get_user_by_name(username)
    if user_info is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not Relation.is_followed(current_user.id, user_info.id):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username, relation=Relation))
    Relation.unfollow(current_user.id, user_info.id)
    flash('You are not following {} anymore.'.format(username))
    return redirect(url_for('.user', username=username, relation=Relation))


@main.route('/followers/<username>')
def followers(username):
    user_info = get_user_by_name(username)
    if user_info is None:
        flash('Invalid user!')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    followers_p = Relation.followers_by_page(user_info.id, page)
    pagination = Pagination(page, followers_p, Relation.followers_count(user_info.id), FOLLOWERS_NUM_PAGE)
    return render_template('followers.html', user=user_info, title='Follower of', endpoint='.followers',
                           pagination=pagination, )


@main.route('/following/<username>')
def following(username):
    pass
