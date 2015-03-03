from bottle import route, run, request, template, redirect, error, static_file, get, response, post
import bottle
import json
import sqlite3

###################OAuth Packages#######################
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
########################################################

#####################GCM Functions######################
from gcm import GCM
gcm = GCM("AIzaSyDrBEVD-RkIKDNWGnt7S6C28tKDIgQk8Xg")

device_token = {}

@post('/registerAndroidDeviceForGCMPush')
def registerAndroidDeviceForGCMPush():
	global device_token
	user_email = request.forms.get("user_email")
	old_token = request.forms.get("old_push_device_token")
	new_token = request.forms.get("new_push_device_token")
	
	if user_email not in device_token:
		print "Adding an entry"
		device_token[user_email] = new_token
	elif user_email in device_token and device_token[user_email] != new_token:
		print "Updating an entry"
		device_token[user_email] = new_token

	data = {}
	data["status"] = "0"
	print device_token
	return json.dumps(data)

@post('/sendTestPush')
def sendTestPush():
	global device_token
	data = {'data': 'This is a test PUSH message'}
	
	# Plaintext request
	#reg_id = 'XXXXXXXXXXXXX'
	#gcm.plaintext_request(registration_id=reg_id, data=data)
	
	# JSON request
	response = gcm.json_request(registration_ids=device_token.values(), data=data)

	# Extra arguments
	#res = gcm.json_request(registration_ids=reg_ids, data=data, collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)

########################################################

#Add in more API's for the server

#Connect to the database
conn = sqlite3.connect('restaurant.sqlite')

#Test to see if the server program works
@route('/test')
def echotest():
	return 'Test successful.'

#Log in a user to the hub (INCOMPLETE)
@route('/login&user=<user>&pwd=8384kvlfsvj023')
def login(user='users'):
	return template('{{user}} has successfully logged into the hub.', user=user)

#Obtain all menu items and their prices of a food place given the restaurant ID
@route('/menu&id=<id:int>')
def location(id):
	menu = conn.cursor()
	
	#Query for a menu's items and their prices given an ID
	menu.execute('SELECT * FROM menu WHERE restaurantID=?', (id,))
	
	#JSON array to store all JSON objects
	data = []
	
	#Store each row of data as a JSON object into the JSON array
	for row in menu:
		data.append({"itemName": row[2], "price": row[3]})
	
	return json.dumps(data)

#Get all basic details for each place on the map
@route('/getAllMapPoints')
def allFoodPlaces():
	places = conn.cursor()
	
	#Query for all restaurants and their locations
	places.execute("SELECT * FROM restaurant")
	
	#JSON array to store all JSON objects
	data = []
	
	#Store each row of data as a JSON object into the JSON array
	for row in places:
		data.append({"restaurant": row[1], "building": row[2], "Longitude": float(row[3]), "Latitude": float(row[4])})

	return json.dumps(data)
	
#Get the review and rating for a given food place
@route('/review+rating&id=<id:int>')
def reviewRating(id):
	reviews = conn.cursor()
	
	#Query for a food place's reviews and ratings
	reviews.execute("SELECT * FROM review WHERE restaurantID=?", (id,))
	
	#JSON array to store all JSON objeccts
	data = []
	
	#Store each row of data as a JSON objet into the JSON array
	for row in reviews:
		data.append({"review": row[2], "rating": row[3], "timestamp": row[4], "user": row[5]})
	
	return json.dumps(data)

######################OAuth Functions#########################
@route('/signIn', 'GET')
def signIn():
	flow = flow_from_clientsecrets("client_secrets.json", scope="https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email", redirect_uri="http://just.test.com:8080/redirect")
	uri = flow.step1_get_authorize_url()
	redirect(str(uri))

@route('/redirect')
def redirect_page():
	code = request.query.get('code', '')
	flow = OAuth2WebServerFlow(client_id="868973567211-me9um9qovn4u9qqc4o624pscvgllqlac.apps.googleusercontent.com", client_secret="4J8V6p3pAzjFuo1JqQErIFd6", scope="https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email", redirect_uri="http://just.test.com:8080/redirect")
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub']

	print "Token: " + token
	http = httplib2.Http()
	http = credentials.authorize(http)

	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = user_document['email']
	user_name = user_document['name']
	
	print "User Name: " + user_name
	print "User Email: " + user_email

	url = "http://192.168.0.109:8080/authorized?user_name=" + user_name + "&user_email=" + user_email
	redirect(url)

@route('/authorized')
def authorized():
	name = request.query.getunicode("user_name", None, "utf8")
	email = request.query.getunicode("user_email", None, "utf8")
	data = {}
	data["status"] = "0"
	data["user_name"] = name
	data["user_email"] = email
	return json.dumps(data)
##############################################################

run(host = "192.168.0.109", port = 8080)
conn.close()