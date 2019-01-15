# -*-coding:utf-8-*-
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
import logging
import sys

import pymysql

pymysql.install_as_MySQLdb()
db = SQLAlchemy()

# scheduler = APScheduler()
logger = logging.getLogger()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    # 指定logger输出格式
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s: %(message)s')

    # 文件日志
    file_handler = logging.FileHandler("log.log")
    file_handler.setFormatter(formatter)

    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter

    # 为logger添加的日志处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 指定日志的最低输出级别，默认为WARN级别
    logger.setLevel(logging.DEBUG)
    # logger.handlers.extend(logging.getLogger("gunicorn.error").handlers)

    from .api import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
