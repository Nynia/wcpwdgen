from app.models import Keyword
import datetime
from app import db


def get_all_keywords():
    items = Keyword.query.all()
    return items


def add_keyword(keyword):
    item = Keyword.query.filter_by(keyword=keyword).first()

    if item:
        return False
    else:
        item = Keyword()
        item.keyword = keyword
        item.createtime = datetime.datetime.now()
        item.modifytime = item.createtime

        db.session.add(item)
        db.session.commit()

        return item
