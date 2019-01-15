from . import api
from flask import jsonify, request
from app.models import Keyword
import datetime
from app import db


@api.route('/keywords', methods=['GET'])
def get_all_keywords():
    items = Keyword.query.all()
    return jsonify(
        {
            'code': '0',
            'msg': 'success',
            'data': [g.to_json() for g in items]
        }
    )


@api.route('/keyword', methods=['POST'])
def add_keyword():
    keyword = request.form.get('keyword')

    item = Keyword.query.filter_by(keyword=keyword).first()

    if item:
        return jsonify(
            {
                'code': '-1000',
                'msg': 'already exists'
            }
        )
    else:
        item = Keyword()
        item.keyword = keyword
        item.createtime = datetime.datetime.now()
        item.createtime = item.createtime

        db.session.add(item)
        db.session.commit()

        return jsonify(
            {
                'code': '0',
                'msg': 'success',
                'data': item.to_json()
            }
        )
