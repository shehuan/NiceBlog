import hashlib
from datetime import datetime

import bleach
from faker import Faker
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Permission:
    """
    权限常量类
    """
    # 喜欢某篇文章
    FAVOURITE = 1
    # 评论
    COMMENT = 2
    # 写博客
    WRITE = 4
    # 管理员
    ADMIN = 8


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
    # 邮箱地址的md5值
    avatar_hash = db.Column(db.String(32))
    blogs = db.relationship('Blog', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    favourites = db.relationship('Favourite', backref='user', lazy='dynamic')
    # 用户权限
    permissions = db.Column(db.Integer)

    def __init__(self, **kw):
        super(User, self).__init__(**kw)
        if self.role is None:
            # 如果是管理员账号，则赋予该user管理员角色
            if self.email == current_app.config['NICEBLOG_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
                self.permissions = 15
            else:
                self.role = Role.query.filter_by(default=True).first()
                self.permissions = 3
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

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
        return self.has_permission(permission)

    def is_administrator(self):
        """
        是否是管理员
        :return:
        """
        return self.can(Permission.ADMIN)

    def can_favourite(self):
        return self.can(Permission.FAVOURITE)

    def can_comment(self):
        return self.can(Permission.COMMENT)

    def ping(self):
        """
        更新最后访问日期
        :return:
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        """
        生成用户头像地址
        :param size:图片大小
        :param default:指定图片生成器
        :param rating:图片级别
        :return:
        """
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,
                                                                     rating=rating)

    def generate_auth_token(self, expiration):
        """
        生成api接口访问的认证令牌
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        """
        检验令牌
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        """
        完成User数据模型到JSON格式化的序列化字典转换
        """
        json_user = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'location': self.location,
            'about_me': self.about_me,
            'member_since': self.member_since,
            'token': self.generate_auth_token(3600 * 24 * 7)
        }
        return json_user

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


class Role(db.Model):
    """
    角色数据Model
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean(), default=False, index=True)
    # 与当前角色相关联的用户组成的列表
    # 'User'：当前Model关联的另一个Model
    # backref='role'：给User添加一个role属性，定义反向关系
    # lazy='dynamic'：不直接加载查询记录，但提供对应的查询功能
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kw):
        super(Role, self).__init__(**kw)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def inset_roles():
        # 定义角色dict
        roles = {
            'User',
            'Administrator'
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            # roles表中没有对应角色，则创建
            if role is None:
                role = Role(name=r)
            # 如果角色名是User，则default为True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


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


class Blog(db.Model):
    """
    博客数据Model
    """
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    # 发布日期
    publish_date = db.Column(db.DateTime, index=True)
    # 最后的编辑日期
    edit_date = db.Column(db.DateTime, index=True)
    # 外键，和User表对应
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 是否是草稿
    draft = db.Column(db.Boolean)
    # 是否禁用评论
    disable_comment = db.Column(db.Boolean, default=False)
    # 被浏览的次数
    views = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='blog', lazy='dynamic')
    favourites = db.relationship('Favourite', backref='blog', lazy='dynamic')

    def is_current_user_favourite(self):
        """
        当前用户是否喜欢了该文章
        """
        if self.favourites and self.favourites.filter_by(user_id=current_user.id).first():
            return True
        else:
            return False

    # @staticmethod
    # def on_changed_content(target, value, oldvalue, initiator):
    #     """
    #     在服务端完成Markdown到Html的转换
    #     """
    #     target.content_html = bleach.linkify(markdown(value, output_format='html',
    #                                                   extensions=['markdown.extensions.extra']))

    def to_json(self):
        """
        完成Blog数据模型到JSON格式化的序列化字典转换
        """
        json_blog = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'content_html': url_for('api.blog_preview', blog_id=self.id, _external=True),
            'publish_date': self.publish_date,
            'labels': [label.name for label in self.labels.all()],
            'views': self.views,
            'comment_count': self.comments.count(),
            'favourite_count': self.favourites.count()
        }
        return json_blog

    @staticmethod
    def fake_blogs(count=50):
        """
        生成测试数据
        :param count:
        :return:
        """
        fake = Faker()
        u = User.query.filter_by(role_id=2).first()
        for i in range(count):
            blog = Blog(title=fake.text()[0:20], summary=fake.text(), content=fake.text(), draft=False,
                        publish_date=datetime.utcnow(), edit_date=datetime.utcnow(), user=u)
            db.session.add(blog)
        db.session.commit()


# 把on_change_content函数注册在content字段上，当content改变时，会执行on_change_content，
# 进而content_html会更新
# db.event.listen(Blog.content, 'set', Blog.on_changed_content)


class Comment(db.Model):
    """
    用户评论的数据模型
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # 该条评论是否已被屏蔽
    disabled = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'))

    @staticmethod
    def on_changed_content(target, value, oldvalue, initiator):
        target.content_html = bleach.linkify(markdown(value, output_format='html',
                                                      extensions=['markdown.extensions.extra']))

    def to_json(self):
        """
        完成User数据模型到JSON格式化的序列化字典转换
        """
        json_comment = {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp,
            'disabled': self.disabled,
            'username': self.user.username,
            'avatar': self.user.gravatar(size=30)
        }
        return json_comment

    @staticmethod
    def fake_comments(count=40):
        fake = Faker()
        u = User.query.filter_by(role_id=1).first()
        blog = Blog.query.filter_by(id=150).first()
        for i in range(count):
            comment = Comment(content=fake.text(), timestamp=fake.past_date(),
                              blog=blog, user=u)
            db.session.add(comment)
        db.session.commit()


db.event.listen(Comment.content, 'set', Comment.on_changed_content)


class Favourite(db.Model):
    """
    喜欢的数据Model
    """
    __tablename__ = 'favourites'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'))

    def to_json(self):
        """
        完成Favourite数据模型到JSON格式化的序列化字典转换
        """
        json_favourite = {
            'id': self.id,
            'timestamp': self.timestamp,
            'blog_id': self.blog.id,
            'blog_title': self.blog.title
        }
        return json_favourite


# Blog和Label多对多关系的中间表
blog_labels = db.Table('blog_labels',
                       db.Column('blog_id', db.Integer, db.ForeignKey('blogs.id')),
                       db.Column('label_id', db.Integer, db.ForeignKey('labels.id')))


class Label(db.Model):
    """
    blog分类标签的Model
    """
    __tablename__ = 'labels'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))
    name = db.Column(db.String(32))
    # 多对多关系模型
    blogs = db.relationship('Blog',
                            secondary=blog_labels,
                            backref=db.backref('labels', lazy='dynamic'),
                            lazy='dynamic')

    def __init__(self, **kw):
        super(Label, self).__init__(**kw)
        types = ['info', 'danger', 'warning', 'success', 'primary', 'default']
        if self.type is None:
            i = (Label.query.count()) % 6
            self.type = types[i]

    def to_json(self):
        """
        完成Label数据模型到JSON格式化的序列化字典转换
        """
        json_label = {
            'id': self.id,
            'name': self.name,
        }
        return json_label
