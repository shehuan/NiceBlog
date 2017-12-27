import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # NICEBLOG_ADMIN = os.environ.get('NICEBLOG_ADMIN')
    # # 发件人
    # NICEBLOG_MAIL_SENDER = 'NiceBlog Admin <othershe.dev.gmail,com>'
    # # 邮件主题前缀
    # NICEBLOG_MAIL_SUBJECT_PREFIX = '[NiceBlog]'

    @staticmethod
    def init_app(app):
        pass


# 针对开发环境的配置
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/niceblog_dev'


# 针对测试环境的配置
class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/niceblog_test'


# 针对生产环境的配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/niceblog'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
