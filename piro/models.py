from piro import db


class User(db.Model):
    userid = db.Column(db.String(120), primary_key=True)#ss
    name = db.Column(db.String(120), unique=False)
    email = db.Column(db.String(120))
    onboarded = db.Column(db.Boolean, unique=False)
    userpimac = db.Column(db.String(120), unique=False)
    #when server recieves a mac, we pull in all userids associated with
    # that mac and then for each user we hit user devices
    #for their respective device auth keys and hit those apis
    # You need to a relationship to Address table here
    # see http://flask-sqlalchemy.pocoo.org/2.1/models/#one-to-many-relationships
    def __init__(self, userid, name, email, onboarded, userpimac):
        self.userid = userid
        self.name = name
        self.email = email
        self.onboarded = onboarded
        self.userpimac = userpimac
    def __repr__(self):
        return "<User %r>" % self.name+\
        "---userid="+self.userid+\
        "---user-email="+self.email+\
        "---onboarded="+self.onboarded+\
        "---userpimac="+self.userpimac

class UserDevice(db.Model):
    userid = db.Column(db.String(120), primary_key=True)#ss
    devicetype = db.Column(db.String(120), primary_key=True) #device example = Fitbit
    deviceusername = db.Column(db.String(120))
    deviceuserid = db.Column(db.String(120))
    accesstoken = db.Column(db.String(120))#ss1 can also be app to fitbitARI
    refreshtoken = db.Column(db.String(120))#ss2
    # You need to a relationship to Address table here
    # see http://flask-sqlalchemy.pocoo.org/2.1/models/#one-to-many-relationships
    def __init__(self, userid, devicetype, deviceusername=None, deviceuserid=None, accesstoken=None, refreshtoken=None):
        self.userid = userid
        self.devicetype = devicetype
        self.deviceusername = deviceusername
        self.deviceuserid = deviceuserid
        self.accesstoken = accesstoken
        self.refreshtoken = refreshtoken
    def __repr__(self):
        return "<User %r>" % self.userid+\
        "---device-type="+self.devicetype+\
        "---device-username="+self.deviceusername+\
        "---device-userid="+self.deviceuserid+\
        "---access-token="+self.accesstoken+\
        "---refresh-token="+self.refreshtoken

