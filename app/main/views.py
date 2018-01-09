from flask import render_template, redirect, url_for, request, current_app, flash
from flask_login import current_user

from app import db
from app.main import main
from app.main.forms import BlogForm, CommentForm
from app.models import User, Blog, Comment


@main.route('/')
def index():
    # 页码
    page = request.args.get('page', 1, type=int)

    # paginate('页码', '每页个数', 'False：超出总页数返回一个空白页，否则404')
    pagination = Blog.query.order_by(Blog.timestamp.desc()).paginate(page=page,
                                                                     per_page=current_app.config['BLOGS_PER_PAGE'],
                                                                     error_out=False)
    blogs = pagination.items
    return render_template('index.html', blogs=blogs, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/create-blog', methods=['GET', 'POST'])
def create_blog():
    form = BlogForm()
    if form.validate_on_submit():
        blog = Blog(title=form.title.data, content=form.content.data, user=current_user._get_current_object())
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('create_blog.html', form=form, type='create')


@main.route('/edit-blog/<int:id>', methods=['GET', 'POST'])
def edit_blog(id):
    blog = Blog.query.get_or_404(id)
    form = BlogForm()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        return redirect(url_for('main.blog', id=id))
    form.title.data = blog.title
    form.content.data = blog.content
    return render_template('create_blog.html', form=form, type='edit')


@main.route('/blog/<int:id>', methods=['GET', 'POST'])
def blog(id):
    blog = Blog.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, blog=blog, user=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('评论成功')
        return redirect(url_for('main.blog', id=id))
    page = request.args.get('page', 1, type=int)
    pagination = blog.comments.order_by(Comment.timestamp.desc()).paginate(page=page,
                                                                           per_page=current_app.config[
                                                                               'COMMENTS_PER_PAGE'],
                                                                           error_out=False)
    comments = pagination.items
    return render_template('blog.html', blog=blog, page=page, comments=comments, pagination=pagination, form=form)
