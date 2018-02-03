from flask import request, current_app, render_template

from app.api import api
from app.api.responses import response
from app.models import Blog, Label


@api.route('/blogs/')
def get_blogs():
    """
    移动端分页请求blog列表的api
    """
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.filter_by(draft=False).order_by(Blog.publish_date.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    blogs = pagination.items
    data = {
        'blogs': [blog.to_json() for blog in blogs],
        'current_page': page,
        'total_page': pagination.total
    }
    return response(data)


@api.route('/labels/<int:label_id>/blogs/')
def get_blogs_by_label(label_id):
    """
    按照标签分页请求blog
    """
    page = request.args.get('page', 1, type=int)
    label = Label.query.filter_by(id=label_id).first()
    pagination = label.blogs.filter_by(draft=False).order_by(Blog.publish_date.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_10'], error_out=False)
    blogs = pagination.items
    data = {
        'blogs': [blog.to_json() for blog in blogs],
        'current_page': page,
        'total_page': pagination.total
    }
    return response(data)


@api.route('/blogs/<int:blog_id>')
def get_blog(blog_id):
    """
    根据id请求文章详情
    """
    blog = Blog.query.get_or_404(blog_id)
    return response(blog.to_json())


@api.route('/blog/preview/<int:blog_id>')
def blog_preview(blog_id):
    """
    为移动端提供的文章html预览页面
    """
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog_preview.html', title=blog.title, content=blog.content_html)
