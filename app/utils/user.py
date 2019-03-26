from app.models import User
import datetime
from app import db


def get_user_by_openid(openid):
    item = User.query.get(openid)
    return item


def add_new_user(openid, email, mode):
    item = User.query.get(openid)
    if item:
        if email is not None:
            item.email = email
        if mode is not None:
            item.mode = mode
    else:
        item = User()
        item.openid = openid
        item.email = email
        item.mode = mode
        item.createtime = datetime.datetime.now()
    item.modifytime = datetime.datetime.now()

    db.session.add(item)
    db.session.commit()
    return True

