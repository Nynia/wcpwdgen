from app.models import User
import datetime
from app import db


def get_user_by_openid(openid):
    item = User.query.get(openid)
    return item


def add_new_user(openid, email, mode=604):
    item = User.query.get(openid)
    if item:
        item.email = email
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


def update_user(openid, email):
    item = User.query.get(openid)
    if item.email1 == email or item.email2 == email or item.email3 == email:
        return False
    if not item.email2:
        item.email2 = email
    elif not item.email3:
        item.email3 = email
    else:
        return False
    item.modifytime = datetime.datetime.now()
    db.session.add(item)
    db.session.commit()

    return True
