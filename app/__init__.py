from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy

from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
# 设置安全等级，防止用户回话被篡改（None,'basic','strong'）
# 设置为strong Flask-Login会记住客户端ip和浏览器的用户代理信息，如果发现异动就登出用户
login_manager.session_protection = 'strong'
# 设置登录页面的端点，
login_manager.login_view = 'auth.login'
# 设置快闪消息，使用@login_required装饰器的路由要用到
login_manager.login_message = '该操作需要先登录账号'

# 客户端实现MarkDown到Html的转换
pagedown = PageDown()

"""
运行时完成程序的创建

默认情况下程序在全局作用域创建，无法动态修改配置，运行脚本时程序已创建，
单元测试时，为了提高测试覆盖，需要在不同环境运行程序，所以要延迟程序的创建，
所以把创建过程移到工厂函数，给脚本留出配置程序的时间，还能创建多个程序实例方便单元测试


把程序的创建转移到工厂函数后，导致定义路由复杂了，
因为程序在运行时创建，只有执行create_app()后才能给视图函数使用app.route()装饰器，
但此时定义路由为时已晚，自定义的错误页面处理视图函数由于使用app_errorhandler()也存在同样问题

需要使用蓝本解决这个问题，在蓝本中定义路由，在蓝本中定义的路由处于休眠状态，直到蓝本注册到程序后，
路由才成为程序的一部分，这里使用结构化方式在包中的多个模块创建蓝本
"""


def create_app(config_name):
    app = Flask(__name__)
    # 导致指定的配置对象
    app.config.from_object(config[config_name])

    # 初始化扩展
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 注册main蓝本
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 注册auth蓝本
    from app.auth import auth as auth_blueprint
    # 使用url_prefix注册后，蓝本中定义的所有路由都会加上指定前缀，/login --> /auth/login
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # 注册manage蓝本
    from app.manage import manage as manage_blueprint
    app.register_blueprint(manage_blueprint, url_prefix='/manage')

    # 注册api蓝本
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
