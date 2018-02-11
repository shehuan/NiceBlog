from flask import flash, request, redirect, url_for, render_template, current_app
from flask_login import login_required, current_user

from app import db
from app.decorators import admin_required
from app.manage import manage
from app.manage.forms import PermissionForm
from app.models import Comment, Favourite, Blog, Role, User, Permission


@manage.route('/comment/disable')
@admin_required
def disable_comment():
    """
    屏蔽某条评论
    """
    id = request.args.get('id', None)
    disable_enable_comment(id, True)
    return '200'


@manage.route('/comment/enable')
@admin_required
def enable_comment():
    """
    恢复某条评论
    """
    id = request.args.get('id', None)
    disable_enable_comment(id, False)
    return '200'


@manage.route('/comment/delete/<int:id>')
@admin_required
def delete_comment(id):
    """
    删除某条评论
    """
    type = request.args.get('type', 1, type=str)
    page = request.args.get('page', 1, type=int)
    comment = Comment.query.get_or_404(id)
    blog_id = comment.blog.id
    db.session.delete(comment)
    db.session.commit()
    flash('已删除该条评论')
    if type == 'manage':
        return redirect(url_for('manage.manage_comments', page=page))
    return redirect(url_for('main.blog', id=blog_id, page=page))


def disable_enable_comment(id, status):
    comment = Comment.query.get_or_404(id)
    comment.disabled = status
    db.session.add(comment)
    db.session.commit()
    return comment.blog.id


@manage.route('/blog/favourite')
@login_required
def favourite_blog():
    """
    喜欢某篇文章
    """
    # 没有喜欢权限
    if not current_user.can_favourite():
        return '403'
    id = request.args.get('id', None)
    blog = Blog.query.get_or_404(id)
    favourite = Favourite(user=current_user, blog=blog)
    db.session.add(favourite)
    db.session.commit()
    return '200'


@manage.route('/blog/cancel_favourite')
@login_required
def cancel_favourite_blog():
    """
    取消喜欢某篇文章
    """
    id = request.args.get('id', None)
    favourite = Favourite.query.filter_by(blog_id=id).first_or_404()
    db.session.delete(favourite)
    db.session.commit()
    return '200'


@manage.route('/blog/my_favourites')
@login_required
def my_favourites():
    """
    我喜欢的文章列表
    """
    page = request.args.get('page', 1, type=int)
    pagination = current_user.favourites.order_by(Favourite.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    favourites = pagination.items
    return render_template('my_favourites.html', favourites=favourites, pagination=pagination)


@manage.route('/users')
@admin_required
def manage_users():
    """
    管理用户
    """
    form = PermissionForm()
    page = request.args.get('page', 1, type=int)
    pagination = Role.query.filter_by(name='User').first().users.paginate(
        page=page, per_page=current_app.config['PER_PAGE_20'], error_out=False)
    users = pagination.items
    return render_template('users.html', form=form, users=users, pagination=pagination, page=page)


@manage.route('/comments')
@admin_required
def manage_comments():
    """
    管理评论
    """
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    comments = pagination.items
    return render_template('comments.html', comments=comments, pagination=pagination, page=page)


@manage.route('/permission/change')
@admin_required
def change_permission():
    """
    更改用户权限，先清空再添加
    """
    favourite = request.args.get('favourite', 0, type=int)
    comment = request.args.get('comment', 0, type=int)
    id = request.args.get('id', None)
    user = User.query.filter_by(id=id).first()
    user.reset_permissions()
    if favourite == 1:
        user.add_permission(Permission.FAVOURITE)
    if comment == 1:
        user.add_permission(Permission.COMMENT)
    db.session.add(user)
    db.session.commit()
    return '200'


@manage.route('/blog/delete/<int:id>')
@admin_required
def delete_blog(id):
    """
    删除文章
    """
    blog = Blog.query.get_or_404(id)
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('main.index'))


@manage.route('/blog/private/<int:id>')
@admin_required
def private_blog(id):
    """
    将已发布的文章私有化，目前设定私有化后会变成草稿
    """
    blog = Blog.query.get_or_404(id)
    blog.draft = True
    db.session.add(blog)
    db.session.commit()
    return redirect(url_for('main.index'))
