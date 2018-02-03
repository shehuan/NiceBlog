from flask import request, g

from app import db
from app.api import api
from app.api.responses import forbidden, response, unauthorized
from app.exceptions import ValidationError
from app.models import User


@api.before_request
def before_request():
    """
    使用before_request钩子进行api接口请求拦截，完整token验证。
    注册、登录、文章预览接口不需要验证
    """
    url = request.url
    if url.find('login') == -1 and url.find('register') == -1 and url.find('preview') == -1:
        token = request.args.get('token')
        if token is None:
            return unauthorized('token缺失')
        user = User.verify_auth_token(token)
        if user is None:
            return forbidden('token过期，请重新登录')
        else:
            # g是程序上下文，用作临时存储对象，
            # 保存当前的请求对应的user，每次请求都会更新
            g.current_user = user


@api.route('/login/', methods=['POST'])
def login():
    """
    登录
    """
    email = request.args.get('email')
    password = request.args.get('password')
    if email is None:
        raise ValidationError('邮箱不能为空')
    if password is None:
        raise ValidationError('密码不能为空')

    user = User.query.filter_by(email=email).first()
    if user is None:
        raise ValidationError('邮箱不存在')
    if user.verify_password(password):
        return response(user.to_json())
    raise ValidationError('密码错误')


@api.route('/register/', methods=['POST'])
def register():
    """
    注册，省去了PC端注册时邮件验证的步骤
    """
    email = request.args.get('email')
    password = request.args.get('password')
    username = request.args.get('username')
    if email is None:
        raise ValidationError('邮箱不能为空')
    if password is None:
        raise ValidationError('密码不能为空')
    if username is None:
        raise ValidationError('昵称不能为空')
    user = User(email=email, username=username, password=password, confirmed=True)
    db.session.add(user)
    db.session.commit()
    return response()
