from datetime import datetime

from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Permission:
    """
    权限常量类
    """
    # 喜欢/收藏
    COLLECT = 1
    # 评论
    COMMIT = 2
    # 写文章
    WRITE = 4
    # 管理员
    ADMIN = 16


class User(UserMixin, db.Model):
    """
    用户数据Model
    """
    # 表名
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # unique=True：字段不允许重复出现，index=True：该字段为索引，提升查询效率
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    # 外键，值为roles表中对应行的id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    # 注册日期，default参数可以用函数作为参数，需要生成默认值时，会调用对应函数
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    # 最后访问日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # 如果是管理员账号，则赋予该user管理员角色
            if self.email == current_app.config['NICEBLOG_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password属性不可读')

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
        return s.dumps({'confirm': self.id}).decode('utf-8')

    # 校验令牌字符串
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # 反序列化
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        """
        重置密码
        :param token:
        :param new_password:
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def can(self, permission):
        """
        权限检查
        :param permission:
        :return:
        """
        return self.role is not None and self.role.has_permission(permission)

    def is_administrator(self):
        """
        是否是管理员
        :return:
        """
        return self.can(Permission.ADMIN)

    def ping(self):
        """
        更新最后访问日期
        :return:
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)


class Role(db.Model):
    """
    角色数据Model
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean(), default=False, index=True)
    permissions = db.Column(db.Integer)
    # 与当前角色相关联的用户组成的列表
    # 'User'：当前Model关联的另一个Model
    # backref='role'：定义反向关系
    # lazy='dynamic'：不直接加载查询记录，但提供对应的查询功能
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def inset_roles():
        # 定义角色对应的权限dict
        roles = {
            'User': [Permission.COLLECT, Permission.COMMIT],
            'Administrator': [Permission.COLLECT, Permission.COMMIT,
                              Permission.WRITE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            # roles表中没有对应角色，则创建
            if role is None:
                role = Role(name=r)
            # 重置权限
            role.reset_permissions()
            # 添加对应角色的权限
            for permission in roles[r]:
                role.add_permission(permission)
            # 如果角色名是User，则default为True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions -= permission

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, permission):
        return self.permissions & permission == permission


class AnonymousUser(AnonymousUserMixin):
    """
    未登录的用户类
    """

    def can(self, permission):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


# Flask-Login的回调函数，用来加载用户信息
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
