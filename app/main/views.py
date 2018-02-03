from datetime import datetime

from flask import render_template, redirect, url_for, request, current_app, flash, abort
from flask_login import current_user, login_required

from app import db
from app.decorators import admin_required
from app.main import main
from app.main.forms import BlogForm, CommentForm
from app.models import User, Blog, Comment, Label


@main.route('/')
def index():
    """
    主页
    """
    # 页码
    page = request.args.get('page', 1, type=int)
    # 全部标签
    labels = Label.query.all()
    label_name = request.args.get('label_name', None, type=str)
    # 按照标签类型查询
    if label_name:
        label = Label.query.filter_by(name=label_name).first()
        pagination = label.blogs.filter_by(draft=False).order_by(Blog.publish_date.desc()).paginate(
            page=page, per_page=current_app.config['PER_PAGE_20'], error_out=False)
        blogs = pagination.items
        return render_template('index.html', blogs=blogs, labels=labels, label_name=label_name, pagination=pagination)

    # paginate('页码', '每页个数', 'False：超出总页数返回一个空白页，否则404')
    pagination = Blog.query.filter_by(draft=False).order_by(Blog.publish_date.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_20'], error_out=False)
    labels = Label.query.all()
    blogs = pagination.items
    return render_template('index.html', blogs=blogs, labels=labels, pagination=pagination)


@main.route('/drafts')
@admin_required
def drafts():
    """
    草稿列表
    """
    # 页码
    page = request.args.get('page', 1, type=int)

    # paginate('页码', '每页个数', 'False：超出总页数返回一个空白页，否则404')
    pagination = Blog.query.filter_by(draft=True).order_by(Blog.edit_date.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_20'], error_out=False)
    blogs = pagination.items
    return render_template('drafts.html', blogs=blogs, pagination=pagination)


@main.route('/user/<username>')
@login_required
def user(username):
    """
    用户个人信息
    """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_info.html', user=user)


@main.route('/create-blog', methods=['GET', 'POST'])
@admin_required
def create_blog():
    """
    写新文章
    """
    form = BlogForm()
    if form.validate_on_submit():
        blog = None
        if form.publish.data:
            blog = Blog(title=form.title.data, summary=form.summary.data, content=form.content.data,
                        content_html=form.preview.data, draft=False, publish_date=datetime.utcnow(),
                        edit_date=datetime.utcnow(), user=current_user._get_current_object())
        elif form.save.data:
            blog = Blog(title=form.title.data, summary=form.summary.data, content=form.content.data,
                        content_html=form.preview.data, draft=True,
                        edit_date=datetime.utcnow(), user=current_user._get_current_object())
        db.session.add(blog)

        new_labels = form.labels.data.split(';')
        add_label(labels=new_labels, blog=blog)

        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('markdown_editor.html', form=form, type='create')


@main.route('/edit-blog/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_blog(id):
    """
    编辑已有文章
    """
    type = request.args.get('type', 1, type=str)
    blog = Blog.query.get_or_404(id)
    form = BlogForm()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.summary = form.summary.data
        blog.content = form.content.data
        blog.content_html = form.preview.data
        blog.edit_date = datetime.utcnow()
        if form.publish.data and type == 'create':
            blog.publish_date = datetime.utcnow()
            blog.draft = False

        db.session.add(blog)
        # 新标签list
        new_labels = form.labels.data.split(' ')

        for label in blog.labels.all():
            # 如果原标签不在新标签list里边，则从标签的blogs属性移除当前blog
            if label.name not in new_labels:
                label.blogs.remove(blog)
                db.session.add(label)
            # 如果原标签在新标签list里边，则不修改原标签，但是从新标签list移除相应标签
            else:
                new_labels.remove(label.name)

        # 给当前blog添加新标签
        add_label(labels=new_labels, blog=blog)

        db.session.commit()
        return redirect(url_for('main.blog', id=id))
    form.title.data = blog.title
    form.labels.data = ' '.join([label.name for label in blog.labels.all()])
    form.summary.data = blog.summary
    form.content.data = blog.content
    return render_template('markdown_editor.html', form=form, type=type)


def add_label(labels, blog):
    for label_item in labels:
        label = Label.query.filter_by(name=label_item).first()
        # labels表中不存在指定名称的标签
        if label is None:
            # 创建新标签
            label = Label(name=label_item)
        label.blogs.append(blog)
        db.session.add(label)


@main.route('/blog/<int:id>', methods=['GET', 'POST'])
def blog(id):
    """
    文章详情
    """
    blog = Blog.query.get_or_404(id)
    blog.views = int(blog.views) + 1
    db.session.add(blog)
    db.session.commit()
    form = CommentForm()
    if form.submit.data:
        # 没有评论权限
        if not current_user.can_comment():
            abort(403)

        if form.validate_on_submit():
            comment = Comment(content=form.content.data, blog=blog, user=current_user._get_current_object())
            db.session.add(comment)
            db.session.commit()
            flash('评论成功')
            return redirect(url_for('main.blog', id=id))
        else:
            flash('评论内容不能为空')
    page = request.args.get('page', 1, type=int)
    pagination = blog.comments.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['PER_PAGE_5'], error_out=False)
    comments = pagination.items
    return render_template('blog.html', blog=blog, page=page, comments=comments, pagination=pagination, form=form,
                           next=request.url)
