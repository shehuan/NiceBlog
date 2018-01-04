from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user

from app import db
from app.main import main
from app.main.forms import WriteBlogForm
from app.models import User, Blog


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


@main.route('/write', methods=['GET', 'POST'])
def write_blog():
    form = WriteBlogForm()
    if form.validate_on_submit():
        blog = Blog(title=form.title.data, body=form.body.data, author=current_user._get_current_object())
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('write_blog.html', form=form)
