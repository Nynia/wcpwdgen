import os

basedir = os.path.abspath(os.path.dirname(__file__))

# weixin
TOKEN = 'CCLOVE'
APPID = 'wx0c3b0b616cc6e6f7'
APPSECRET = '7ca986e41bd99f50547e302a485d4643'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'skks'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://ubuntu:ubuntu123@127.0.0.1/weixinpwd'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:admin@35.246.68.36/weixinpwd'


config = {
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': TestingConfig
}
