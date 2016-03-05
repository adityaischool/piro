#Main submodule to enable WSGI and Flask initialise

from flask import Flask
app = Flask(__name__)
print "configuring now"
#print ";;;;;;;"+app.config['Callback']
