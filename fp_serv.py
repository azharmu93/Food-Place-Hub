from bottle import route, run, request, template, redirect, error, static_file, get, response, post
import bottle
import json
import sqlite3
from datetime import datetime

# ##################OAuth Packages#######################
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
# #######################################################

# ####################GCM Functions######################
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

# #######################################################

# TODO:
# Change the HTTP GET's to HTTP POST's

# Connect to the database
conn = sqlite3.connect('restaurant.sqlite')
cursor = conn.cursor()

# Test to see if the server program works
@route('/test')
def echotest():
	test = ["Test successful"]
	
	json.dumps(test)

# ############### ADMIN CLIENT API's ############### #

# Register a new admin to the hub
@post('/register&user=<user>&pwd=<pwd>&placeName=<name>')
def register(user, pwd, name):
	newID = 0

	# 1. Create the new food place entries in the database
	cursor.execute("SELECT max(restaurantID) FROM restaurant")
	if cursor != None:
		maxID = cursor.fetchone()
		newID = maxID[0] + 1
		
	
	
	# 2. Create the login entry for the new admin user

	#Insert the user's login credentials into the database in order to register the user
	cursor.execute("INSERT INTO loginCredentials VALUES(?,?,?)", (user,pwd,name,))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)

# Log in an admin to the hub
@post('/login&user=<user>&pwd=<pwd>')
def login(user, pwd):
	#Search for the user with the specified password
	cursor.execute("SELECT * FROM loginCredentials WHERE user = ? AND password = ?", (user,pwd,))
	
	check = login.fetchone()
	
	#Set up a JSON object to store return values
	# 0: success
	# non-zero value: failure
	ack = []
	
	if check == None: #Login was unsuccessful
		ack.append({"result": 0})
	else: #Login was successful
		ack.append({"result": 0})
	
	return json.dumps(ack)
	
@post('/addDetails&placeID=<id:int>&description=<desc>&cuisineType=<cuisType>&hoursOfOperation=<hoursOp>')
def addDetails(id, desc, cuistype, hoursOp):
	#Add the description for the given food place into the database
	cursor.execute("INSERT INTO restaurantDetails VALUES(?,?,?,?)", (id, desc, cuisType, hoursOp))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)
	
@post('/updateDescription&placeID=<id:int>&description=<desc>')
def updateDescription(id, desc):
	#Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET description = ? WHERE restaurantID = ?", (desc, id))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)

@post('/updateCuisineType&placeID=<id:int>&cuisineType=<type>')
def updateCuisineType(id, type):
	#Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET cuisineType = ? WHERE restaurantID = ?", (type, id))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)

@post('/updateHours&placeID=<id:int>&hours=<hours>')
def updateDescription(id, hours):
	#Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET hoursOfOperation = ? WHERE restaurantID = ?", (hours, id))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)
	
# ############### USER CLIENT API's ############### #

# Obtain all menu items and their prices of a food place given the restaurant ID
@post('/getMenuItems')
def location():
	placeID = request.forms.get("placeID")
	
	#Query for a menu's items and their prices given an ID
	cursor.execute("SELECT * FROM menu WHERE restaurantID=?", (placeID,))
	
	#JSON array to store all JSON objects
	data = []
	
	#Store each row of data as a JSON object into the JSON array
	for row in cursor:
		data.append({"itemName": row[2], "price": row[3]})
	
	return json.dumps(data)

# Get all basic details for each place on the map
@post('/getAllPoints')
def allFoodPlaces():
	#Query for all restaurants and their locations
	cursor.execute("SELECT * FROM restaurant")
	
	#JSON array to store all JSON objects
	data = []
	
	#Store each row of data as a JSON object into the JSON array
	for row in cursor:
		data.append({"restaurant": row[1], "building": row[2], "Longitude": float(row[3]), "Latitude": float(row[4])})

	return json.dumps(data)

@post('/getPlaceDetails')
def getPlaceDetails():
	# Find the largest review ID for the given food place
	cursor.execute("SELECT max(reviewID) FROM review")
	entry = cursor.fetchone()
	maxReviewID = entry[0]
	
	placeID = request.forms.get("placeID")
	
	#Query to get a food place's details
	cursor.execute("SELECT * FROM restaurantDetails WHERE restaurantID = ?", (placeID,))
	
	data = []
	
	for row in cursor:
		data.append({"description": row[1], "cuisineType": row[2], "hoursOfOperation": row[3], "phoneNum": row[4]})
		
	#Query to get the food place's first five reviews
	cursor.execute("SELECT * FROM review WHERE restaurantID = ? AND reviewID > 0 AND reviewID < 6", (placeID,))
	
	for row in cursor:
		if row[1] < maxReviewID:
			data.append({"review": row[2], "rating": row[3], "timestamp": row[4], "user": row[5], "end": 0})
		else:
			data.append({"review": row[2], "rating": row[3], "timestamp": row[4], "user": row[5], "end": 1})
		
	return json.dumps(data)
	
# Get the review and rating for a given food place
@post('/getMoreReviews')
def reviewRating():
	# Find the largest review ID for the given food place
	cursor.execute("SELECT max(reviewID) FROM review")
	entry = cursor.fetchone()
	maxReviewID = entry[0]
	
	placeID = request.forms.get("placeID")
	index = request.forms.get("index")
	
	#Query for a food place's reviews and ratings
	cursor.execute("SELECT * FROM review WHERE restaurantID = ? AND reviewID > (? * 5) AND reviewID <= ((? + 1) * 5) ", (placeID,index,index,))
	
	#JSON array to store all JSON objects
	data = []
	
	#Store each row of data as a JSON object into the JSON array
	for row in cursor:
		if row[1] < maxReviewID:
			data.append({"review": row[2], "rating": row[3], "timestamp": row[4], "user": row[5], "end": 0})
		else:
			data.append({"review": row[2], "rating": row[3], "timestamp": row[4], "user": row[5], "end": 1})
	
	return json.dumps(data)
	
@post('/submitReview')
def submitReview():
	newID = 0
	
	# Find the largest review ID for the given food place
	cursor.execute("SELECT max(reviewID) FROM review")
	if cursor != None:
		maxID = cursor.fetchone()
		newID = maxID[0] + 1
	
	# Get the current timestamp
	current_time = datetime.now().strftime("%Y/%m/%d %I:%M%p")
	
	placeID = request.forms.get("placeID")
	rating = request.forms.get("rating")
	comments = request.forms.get("comments")
	submitBy = request.forms.get("submitBy")
	
	#Insert a review and rating for a given food place from a given user
	cursor.execute("INSERT INTO review VALUES(?,?,?,?,?,?)", (placeID,newID,comments,rating,current_time,submitBy,))
	
	#Commit the changes to the database
	conn.commit()
	
	# Set up a JSON object with a return value
	# 0: success
	# non-zero value: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)
	
@post('/addSubscription')
def addSubscription():
	user_email = request.forms.get("user_email")
	deviceID = request.forms.get("deviceID")
	
	# Insert the new subscription into the database
	cursor.execute("INSERT INTO subscription VALUES(?,?)", (user_email,deviceID,))
	
	#Commit the changes to the database
	conn.commit()
	
	# Set up a JSON object with a return value
	# 0: success
	# non-zero value: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)
	
@post('/removeSubscription')
def removeSubscription():
	user_email = request.forms.get("user_email")
	deviceID = request.forms.get("deviceID")
	
	#Delete the entry containing the user and the device ID associated with that user
	cursor.execute("DELETE FROM subscription WHERE user_email = ? AND deviceID = ?", (user_email,deviceID,))
	
	#Commit the changes to the database
	conn.commit()
	
	# Set up a JSON object with a return value
	# 0: success
	# non-zero value: failure
	ack = []
	ack.append({"result": 0})
	
	return json.dumps(ack)

run(host = "localhost", port = 8080)

conn.close()