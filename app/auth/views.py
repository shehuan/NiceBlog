# app.route()装饰器把修饰的视图函数注册为路由
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_email
from app.models import User


@auth.before_app_request
def before_request():
    """
    过滤未进行邮件确认的账户，会在请求之前调用
    :return:
    """
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    登录
    """
    if current_user.is_authenticated:
        flash('您已经登录')
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('用户不存在')
        elif user.verify_password(form.password.data):
            # 在用户会话中把用户标记为已登录，参数为当前用户以及是否记住我的布尔值，
            # 如果布尔值为False则关闭浏览器后会话过期，下次访问需重新登录，
            # 如果为True，则会在浏览器中写入一个cookie，来复现用户会话
            login_user(user, form.remember_me.data)
            # 此处的重定向有两种
            # 1.访问未授权的URL会显示登录页面，flask_login会把原地址保存在next参数中，登录成功后转到原地址
            # 2.next参数不存在，则转到首页
            # url_for：获取视图函数的URL
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('用户名或密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """
    登出
    """
    # 删除并重置用户会话
    logout_user()
    flash('您已经退出登录')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    注册
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        # 发送确认邮件
        send_email(user.email, '账号信息确认', 'auth/email/confirm', user=user, token=token)
        flash("已发送信息确认邮件，请注意查收")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """
    邮件确认
    """
    # 已经通过邮件链接确认，则重定向到首页
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    # 进行邮件链接检验
    if current_user.confirm(token):
        db.session.commit()
        flash('账号信息确认成功')
    else:
        flash('账号信息确认失败，链接无效')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """
    重新发送账号确认邮件
    :return: 
    """
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '账号信息确认', 'auth/email/confirm', user=current_user, token=token)
    flash('邮件已发送，请注意查收')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    """
    未进行邮件验证，登录后的视图函数
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    修改密码
    :return:
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if form.new_password.data == form.old_password.data:
            flash('新密码不能和原始密码相同')
        elif current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('密码修改成功')
            return redirect(url_for('main.index'))
        else:
            flash('原始密码错误')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    """
    重置密码：邮件验证
    :return:
    """
    # 不是匿名用户，则跳转到首页
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置密码', 'auth/email/reset_password', user=user, token=token,
                       next=request.args.get('next'))
            flash('重置密码邮件已发送，请注意查收')
            redirect(url_for('auth.login'))
        else:
            flash('用户不存在')
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    重置密码：设置新密码
    :return:
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('重置密码成功')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
