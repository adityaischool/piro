from piro import db


class User2(db.Model):
    userid = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(120), unique=False)
    email = db.Column(db.String(120))
    # You need to a relationship to Address table here
    # see http://flask-sqlalchemy.pocoo.org/2.1/models/#one-to-many-relationships
    def __init__(self, userid, name, email):
        self.userid=userid
        self.name = name
        self.email = email
    def __repr__(self):
        return '<Customer %r>' % self.email

class UserDevice2(db.Model):
    userid = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(120), unique=False)
    email = db.Column(db.String(120))
    # You need to a relationship to Address table here
    # see http://flask-sqlalchemy.pocoo.org/2.1/models/#one-to-many-relationships
    def __init__(self, userid, name, email):
        self.userid=userid
        self.name = name
        self.email = email
    def __repr__(self):
        return '<Customer %r>' % self.email