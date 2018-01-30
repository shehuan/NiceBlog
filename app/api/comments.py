from flask import request, current_app, jsonify, g, url_for

from app import db
from app.api import api
from app.decorators import permission_required
from app.models import Blog, Comment, Permission, User


@api.route('/blogs/<int:blog_id>/comments')
def get_comments(blog_id):
    """
    分页请求对应id的文章的评论
    """
    page = request.args.get('page', 1, type=int)
    blog = Blog.query.get_or_404(blog_id)
    pagination = blog.comments.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    comments = pagination.items
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'current_page': page,
        'total_page': pagination.total
    })


@api.route('/users/<int:user_id>/comments')
def get_user_comments(user_id):
    """
    分页请求对应id的用户发表的评论
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(user_id)
    pagination = user.comments.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    comments = pagination.items
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'current_page': page,
        'total_page': pagination.total
    })


@api.route('/blogs/<int:blog_id>/comment/', methods=['POST'])
@permission_required(Permission.COMMENT)
def add_comment(blog_id):
    """
    提交评论
    """
    blog = Blog.query.get_or_404(blog_id)
    comment = Comment.from_json(request.json)
    comment.user = g.current_user
    comment.blog = blog
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'code': 6000,
        'message': 'success',
        'data': ''
    })
