import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    NICEBLOG_ADMIN = os.environ.get('NICEBLOG_ADMIN')
    NICEBLOG_MAIL_SENDER = 'NiceBlog Admin <othershe.dev.gmail,com>'
    NICEBLOG_MAIL_SUBJECT_PREFIX = '[NiceBlog]'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
