from flask import flash, request, redirect, url_for, render_template, current_app
from flask_login import login_required, current_user

from app import db
from app.decorators import admin_required
from app.manage import manage
from app.manage.forms import PermissionForm
from app.models import Comment, Favourite, Blog, Role, User


@manage.route('/comment/disable/<int:id>')
@admin_required
def disable_comment(id):
    """
    屏蔽某条评论
    """
    type = request.args.get('type', 1, type=str)
    page = request.args.get('page', 1, type=int)
    blog_id = disable_enable_comment(id, True)
    flash('已屏蔽该条评论')
    if type == 'manage':
        return redirect(url_for('manage.manage_comments', page=page))
    return redirect(url_for('main.blog', id=blog_id, page=page))


@manage.route('/comment/enable/<int:id>')
@admin_required
def enable_comment(id):
    """
    恢复某条评论
    """
    type = request.args.get('type', 1, type=str)
    page = request.args.get('page', 1, type=int)
    blog_id = disable_enable_comment(id, False)
    flash('已恢复该条评论')
    if type == 'manage':
        return redirect(url_for('manage.manage_comments', page=page))
    return redirect(url_for('main.blog', id=blog_id, page=page))


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


@manage.route('/blog/favourite/<int:id>')
@login_required
def favourite_blog(id):
    """
    喜欢某篇文章
    """
    blog = Blog.query.get_or_404(id)
    favourite = Favourite(user=current_user, blog=blog)
    db.session.add(favourite)
    db.session.commit()
    return redirect(url_for('main.blog', id=id))


@manage.route('/blog/cancel_favourite/<int:id>')
@login_required
def cancel_favourite_blog(id):
    """
    取消喜欢某篇文章
    """
    favourite = Favourite.query.filter_by(blog_id=id).first_or_404()
    db.session.delete(favourite)
    db.session.commit()
    return redirect(url_for('main.blog', id=id))


@manage.route('/blog/my_favourites')
@login_required
def my_favourites():
    """
    我喜欢的文章列表
    """
    page = request.args.get('page', 1, type=int)
    pagination = current_user.favourites.order_by(Favourite.timestamp.desc()).paginate(
        page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
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
    pagination = Role.query.filter_by(name='User').first().users.paginate(page,
                                                                          per_page=current_app.config['PER_PAGE_20'],
                                                                          error_out=False)
    users = pagination.items
    return render_template('users.html', form=form, users=users, pagination=pagination, page=page)


@manage.route('/comments')
@admin_required
def manage_comments():
    """
    管理评论
    """
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page,
                                                                           per_page=current_app.config['PER_PAGE_10'],
                                                                           error_out=False)
    comments = pagination.items
    return render_template('comments.html', comments=comments, pagination=pagination, page=page)


@manage.route('/permission/add/<int:id>')
@admin_required
def add_permission(id):
    """
    添加权限
    """
    page = request.args.get('page', 1, type=int)
    permission = request.args.get('permission', 0, type=int)
    add_remove_permission(id=id, permission=permission, type='add')
    return redirect(url_for('manage.manage_users', page=page))


@manage.route('/permission/remove/<int:id>')
@admin_required
def remove_permission(id):
    """
    移除权限
    """
    page = request.args.get('page', 1, type=int)
    permission = request.args.get('permission', 0, type=int)
    add_remove_permission(id=id, permission=permission, type='remove')
    return redirect(url_for('manage.manage_users', page=page))


def add_remove_permission(id, permission, type):
    user = User.query.filter_by(id=id).first()
    if type == 'add':
        user.role.add_permission(permission)
    else:
        user.role.remove_permission(permission)
    db.session.add(user)
    db.session.commit(user)
