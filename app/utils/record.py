from app.models import Record
import datetime
from app import db


def add_new_record(openid, content):
    record = Record()
    record.content = content
    record.openid = openid
    record.createtime = datetime.datetime.now()

    db.session.add(record)
    db.session.commit()
