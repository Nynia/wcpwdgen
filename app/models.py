from app import db


class User(db.Model):
    __tablename__ = 'user'
    openid = db.Column(db.VARCHAR(50), primary_key=True)
    email1 = db.Column(db.VARCHAR(50))
    email2 = db.Column(db.VARCHAR(50))
    email3 = db.Column(db.VARCHAR(50))
    createtime = db.Column(db.DATETIME)
    modifytime = db.Column(db.DATETIME)

    def to_json(self):
        return {
            'openid': self.openid,
            'email1': self.email1,
            'email2': self.email2,
            'email3': self.email3,
            'createtime': self.createtime,
            'modifytime': self.modifytime
        }

    def __repr__(self):
        return '<User %r>' % self.openid


class Master(db.Model):
    __tablename__ = 'master'
    id = db.Column(db.INTEGER, primary_key=True)
    openid = db.Column(db.VARCHAR(50))
    keyword = db.Column(db.VARCHAR(50))
    account = db.Column(db.VARCHAR(50))
    mode = db.Column(db.INTEGER)
    createtime = db.Column(db.DATETIME)
    modifytime = db.Column(db.DATETIME)

    def to_json(self):
        return {
            'id': self.id,
            'openid': self.openid,
            'keyword': self.keyword,
            'account': self.account,
            'mode': self.mode,
            'createtime': self.createtime,
            'modifytime': self.modifytime
        }


class Keyword(db.Model):
    __tablename__ = 'keyword'
    id = db.Column(db.INTEGER, primary_key=True)
    keyword = db.Column(db.VARCHAR(50))
    label1 = db.Column(db.VARCHAR(50))
    label2 = db.Column(db.VARCHAR(50))
    createtime = db.Column(db.DATETIME)
    modifytime = db.Column(db.DATETIME)

    def to_json(self):
        return {
            'id': self.id,
            'keyword': self.keyword,
            'label1': self.label1,
            'label2': self.label2,
            'createtime': self.createtime,
            'modifytime': self.modifytime
        }

    def __repr__(self):
        return '<Keyword %r>' % self.keyword


class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.INTEGER, primary_key=True)
    openid = db.Column(db.VARCHAR(50))
    content = db.Column(db.VARCHAR(50))
    createtime = db.Column(db.DATETIME)

    def to_json(self):
        return {
            'id': self.id,
            'openid': self.openid,
            'content': self.content,
            'createtime': self.createtime
        }

    def __repr__(self):
        return '<Record %r>' % self.content
