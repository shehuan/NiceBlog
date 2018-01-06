from flask import flash, request, redirect, url_for
from flask_login import login_required

from app import db
from app.decorators import admin_required
from app.manage import manage
from app.models import Comment


@manage.route('/comment/disable/<int:id>')
@admin_required
@login_required
def disable_comment(id):
    """
    屏蔽评论
    :return:
    """
    blog_id = disable_enable_comment(id, False)
    flash('已屏蔽该条评论')
    return redirect(url_for('main.blog', id=blog_id,
                            page=request.args.get('page', 1, type=int)))


@manage.route('/comment/enable/<int:id>')
@admin_required
@login_required
def enable_comment(id):
    """
    恢复评论
    :return:
    """
    blog_id = disable_enable_comment(id, True)
    flash('已恢复该条评论')
    return redirect(url_for('main.blog', id=blog_id,
                            page=request.args.get('page', 1, type=int)))


def disable_enable_comment(id, status):
    comment = Comment.query.get_or_404(id)
    comment.disabled = status
    db.session.add(comment)
    db.session.commit()
    return comment.blog.id
