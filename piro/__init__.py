#Main submodule to enable WSGI and Flask initialise

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
import metaclient

print "initializing flask app"
app = Flask(__name__)
CORS(app)
app.config.from_object('config')
db = SQLAlchemy(app)
print "configuring now"

#print "APPPP",app['FITBIT_CL_ID']
from piro import views, models
from piro import db
db.create_all()
