#Main submodule to enable WSGI and Flask initialise

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
print "configuring now"


from piro import views, models
#>>> from piro import db
#>>> db.create_all()
