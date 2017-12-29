from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    # 表名
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # unique=True：字段不允许重复出现，index=True：该字段为索引，提升查询效率
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 计算密码的散列值
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 核对密码，即比较输入密码的散列值和原密码的散列值
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成令牌字符串
    # 初次注册时发送用户信息确认邮件需要使用
    def generate_confirmation_token(self, expiration=3600):
        # 生成有过期时间的签名
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        # 序列化
        return s.dumps({'confirm': self.id})

    # 校验令牌字符串
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 反序列化
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True


# Flask-Login的回调函数，用来加载用户信息
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
