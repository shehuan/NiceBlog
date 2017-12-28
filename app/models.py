from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    # 表名
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # unique=True：字段不允许重复出现，index=True：该字段为索引，提升查询效率
    name = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

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


# Flask-Login的回调函数，用来加载用户信息
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
