from flask import g, jsonify, request
from flask_httpauth import HTTPBasicAuth

from app.api import api
from app.api.errors import unauthorized, forbidden
from app.models import User

"""
初始化HTTP认证扩展，只有api接口需要，所以只在蓝本初始化
"""
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """
    检验用户口令，校验失败则HTTPAuth默认返回401，但可以自定义改错误

    如果email_or_token不为空，password为空，则认为是要通过令牌进行认证
    如果两个都不为空则认为是通过普通的邮箱密码方式进行认证
    至于如何认证则由用户决定
    :param email_or_token: 邮箱地址或者认证令牌
    :param password: 密码
    :return:
    """
    print(email_or_token, password)
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        # g.token_used 记录是否是令牌认证
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """
    自定义检验失败的401错误
    """
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    """
    进行统一的用户认证，拒绝已通过认证但未进行账户确认的用户
    """
    print('before_request')
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600 * 24 * 7)})


@api.route('/login', methods=['POST'])
def login():
    email = request.args.get('email')
    password = request.args.get('password')
    pass


@api.route('/register', methods=['POST'])
def register():
    email = request.args.get('email')
    password = request.args.get('password')
    pass
