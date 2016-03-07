from flask import render_template,request,session,redirect,jsonify,Response
from flask import url_for
from piro import app
import urllib2,fitoauth
import math
import json,os,requests,os,datetime,time
from flask import Response
#from libraries.python-fitbit-master import foauth2
from libraries import pythonfitbitmaster as pythonfitbitmaster
from libraries.pythonfitbitmaster import foauth2
import fitbit
from models import UserDevice,User
from piro import hitFitbitApi
#import request

@app.route('/', methods=['GET', 'POST'])
def land():
	return render_template("index.html")


@app.route('/requestdata', methods=['GET', 'POST'])
def upload():
	print "requested data"
	if request.method == 'POST':
		macaddress = request.form['macaddress']
	else:
		macaddress=request.args.get("macaddress")
	print "\n requested data by mac address---",macaddress
	try:
		print "sending to parse data"
		js=parsedata(macaddress)
	except Exception as e:
		print e
		return ''
	print "returning response"
	return Response(json.dumps(js))

def parsedata(macaddress):
	userswithMac=User.query.filter_by(userpimac=macaddress).first()
	fdict=userswithMac.__dict__
	print "dict for this mac is", fdict
	userpimac=fdict['userpimac']
	userid=fdict['userid']
	print"mac address translated to this user----",userid
	js=hitFitbitApi.hitFitbitApis(userid)
	print "gonna return",js
	return js
	

@app.route('/register', methods=['GET', 'POST'])
def register():
	userid=request.args.get("name")
	print "userid is ----- -        ", userid
	foauth2.fitbitoauth(userid)
	return render_template("register.html")

@app.route('/getdata', methods=['GET', 'POST'])
def getdata():
	#user makes get request to our api with param userid=* and auth
	userid=request.args.get("userid")
	try:
		first=UserDevice.query.filter_by(userid=userid).first()
	except Exception as e:
		print e
		return ''
	print "user id is ----",userid
	print "first row is ----"
	print first.__dict__
	fdict=first.__dict__
	accesstoken=fdict['accesstoken']
	refreshtoken=fdict['refreshtoken']
	#aut_cl=Fitbit('994ae27440a52d1f0bb33e8d7e305929','d7a4ececd5e68a5f3f36d64e304fbe25',oauth2=True,access_token=accesstoken,refresh_token=refreshtoken)
	aut_cl=fitbit.Fitbit('227NKT','d7a4ececd5e68a5f3f36d64e304fbe25',oauth2=True,access_token=accesstoken,refresh_token=refreshtoken)
	print "-----------\n-----\n---activities-----\n\n\n"
	print aut_cl.activities(date='2015-12-24')
	return render_template("index.html")


@app.route('/fitbit', methods=['GET', 'POST'])
def fitbithandler():
	#call fitbit oauth code here
	foauth2.fitbitoauth()
	"""z = fitoauth.Fitbit()
	auth_url = z.GetAuthorizationUri()
	print "AAAAuth URL",auth_url
	#accesscode=auth_url['access_code']
	token = z.GetAccessToken(access_code)
	response = z.ApiCall(token, '/1/user/-/activities/log/steps/date/today/7d.json')
	print "response",response
	#foauth2.newauth()"""
	return render_template("index.html")

@app.route('/fitbit2', methods=['GET', 'POST'])
def fitbithandler2():
	#call fitbit oauth code here
	#foauth2.fitbitoauth()
	z = fitoauth.Fitbit()
	auth_url = z.GetAuthorizationUri()
	print "AAAAuth URL",auth_url
	accesscode=auth_url['access_code']
	token = z.GetAccessToken(access_code)
	response = z.ApiCall(token, '/1/user/-/activities/log/steps/date/today/7d.json')
	print "response",response
	#foauth2.newauth()"""
	return render_template("index.html")