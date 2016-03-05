from flask import render_template,request,session,redirect,jsonify,Response
from flask import url_for
from piro import app
import urllib2
import math
import json,os,requests,os,datetime,time
from flask import Response
#import request

@app.route('/', methods=['GET', 'POST'])
def land():
	return render_template("index.html")


