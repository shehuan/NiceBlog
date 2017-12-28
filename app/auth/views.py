# app.route()装饰器把修饰的视图函数注册为路由
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required

from app.auth import auth
from app.auth.forms import LoginForm
from app.models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # 在用户会话中把用户标记为已登录，参数为当前用户以及是否记住我的布尔值，
            # 如果布尔值为False则关闭浏览器后会话过期，下次访问需重新登录，
            # 如果为True，则会在浏览器中写入一个cookie，来复现用户会话
            login_user(user, form.remember_me.data)
            # 此处的重定向有两种
            # 1.访问未授权的URL会显示登录页面，flask_login会把原地址保存在next参数中，登录成功后转到原地址
            # 2.next参数不存在，则转到首页
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    # 删除并重置用户会话
    logout_user()
    flash('您已经退出登录！')
    return redirect('main.index')
