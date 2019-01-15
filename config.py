import os

basedir = os.path.abspath(os.path.dirname(__file__))

# weixin
TOKEN = 'CCLOVE'
APPID = 'wx0c3b0b616cc6e6f7'
APPSECRET = '0333eabbe733dd2c86c6532893271137'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'skks'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:admin@127.0.0.1/wc_pwd'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:admin@35.230.143.112/wc_pwd'


config = {
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': TestingConfig
}
