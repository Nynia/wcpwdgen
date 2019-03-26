from app.models import Keyword
import datetime
from app import db


def get_all_keywords():
    items = Keyword.query.all()
    return items


def add_keyword(keyword, label1, label2):
    item = Keyword.query.filter_by(keyword=keyword).first()

    if item:
        if label1 is not None:
            item.label1 = label1
        if label2 is not None:
            item.label2 = label2
    else:
        item = Keyword()
        item.keyword = keyword
        item.label1 = label1
        item.label2 = label2
        item.createtime = datetime.datetime.now()
        item.modifytime = item.createtime

        db.session.add(item)
        db.session.commit()

        return item
