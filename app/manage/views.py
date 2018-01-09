from flask import flash, request, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.decorators import admin_required
from app.manage import manage
from app.models import Comment, Favourite, Blog


@manage.route('/comment/disable/<int:id>')
@admin_required
def disable_comment(id):
    """
    屏蔽评论
    """
    blog_id = disable_enable_comment(id, True)
    flash('已屏蔽该条评论')
    return redirect(url_for('main.blog', id=blog_id,
                            page=request.args.get('page', 1, type=int)))


@manage.route('/comment/enable/<int:id>')
@admin_required
def enable_comment(id):
    """
    恢复评论
    """
    blog_id = disable_enable_comment(id, False)
    flash('已恢复该条评论')
    return redirect(url_for('main.blog', id=blog_id,
                            page=request.args.get('page', 1, type=int)))


@manage.route('/comment/delete/<int:id>')
@admin_required
def delete_comment(id):
    """
    删除评论
    """
    comment = Comment.query.get_or_404(id)
    blog_id = comment.blog.id
    db.session.delete(comment)
    db.session.commit()
    flash('已删除该条评论')
    return redirect(url_for('main.blog', id=blog_id,
                            page=request.args.get('page', 1, type=int)))


def disable_enable_comment(id, status):
    comment = Comment.query.get_or_404(id)
    comment.disabled = status
    db.session.add(comment)
    db.session.commit()
    return comment.blog.id


@manage.route('/blog/favourite/<int:id>')
@login_required
def favourite_blog(id):
    blog = Blog.query.get_or_404(id)
    favourite = Favourite(user=current_user, blog=blog)
    db.session.add(favourite)
    db.session.commit()
    return redirect(url_for('main.blog', id=id))


@manage.route('/blog/cancel_favourite/<int:id>')
@login_required
def cancel_favourite_blog(id):
    favourite = Favourite.query.filter_by(blog_id=id).first_or_404()
    db.session.delete(favourite)
    db.session.commit()
    return redirect(url_for('main.blog', id=id))
