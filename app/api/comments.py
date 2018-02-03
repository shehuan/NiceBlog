from flask import request, current_app, g

from app import db
from app.api import api
from app.api.decorators import comment_required
from app.api.responses import response
from app.exceptions import ValidationError
from app.models import Blog, Comment, User


@api.route('/blogs/<int:blog_id>/comments/')
def get_comments(blog_id):
    """
    分页请求对应id的文章的评论
    """
    page = request.args.get('page', 1, type=int)
    blog = Blog.query.get_or_404(blog_id)
    pagination = blog.comments.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    comments = pagination.items
    data = {
        'comments': [comment.to_json() for comment in comments],
        'current_page': page,
        'total_page': pagination.total
    }
    return response(data)


@api.route('/users/<int:user_id>/comments/')
def get_user_comments(user_id):
    """
    分页请求对应id的用户发表的评论
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(user_id)
    pagination = user.comments.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    comments = pagination.items
    data = {
        'comments': [comment.to_json() for comment in comments],
        'current_page': page,
        'total_page': pagination.total
    }
    return response(data)


@api.route('/blogs/<int:blog_id>/comment/', methods=['POST'])
@comment_required
def add_comment(blog_id):
    """
    提交评论
    """
    content = request.args.get('content')
    if content is None or content == '':
        raise ValidationError('评论内容不能为空')
    blog = Blog.query.get_or_404(blog_id)
    comment = Comment(content=content, blog=blog, user=g.current_user)
    db.session.add(comment)
    db.session.commit()
    return response()
