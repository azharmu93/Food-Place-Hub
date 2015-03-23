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
counter = 0
device_token = {}
#device_token["zombies"] = "APA91bGo5vKYBGxhdh5xP_uFfaCYDNaVo3mKZfkYgacex2fR6U0OSBDQypn8lfne6N7oCGTsYAUIw97ooUjI7HcayDuu04Xl4axxCEaVxjYw58UM8AOxoI6SxQExTdo-YpXp7xJvAId4Q3xUXGKWGBjdIK4gnjySkg"

@post('/registerAndroidDeviceForGCMPush')
def registerAndroidDeviceForGCMPush():
	global device_token
	user_email = request.forms.get("user_email")
	old_token = request.forms.get("old_push_device_token")
	new_token = request.forms.get("new_push_device_token")
	
	if user_email not in device_token:
		device_token[user_email] = new_token
	elif user_email in device_token and device_token[user_email] != new_token:
		device_token[user_email] = new_token

	data = {}
	data["status"] = "0"
	print device_token
	return json.dumps(data)

@post('/sendTestPush')
def sendTestPush():
	global device_token
	global counter
	if (counter % 5) == 0:
		data = {'messageTitle': 'Daily Special', "restaurant": 'SpringRoll SS', 'data': 'This is a test PUSH message'}
	elif (counter % 5) == 1:
		data = {'messageTitle': 'Daily Special', "restaurant": 'Veda', 'data': 'There is a new menu item'}
	elif (counter % 5) == 2:
		data = {'messageTitle': 'Daily Special', "restaurant": 'Cube', 'data': 'Drinks on sale after 4PM'}
	elif (counter % 5) == 3:
		data = {'messageTitle': 'Daily Special', "restaurant": 'SpringRoll MSB', 'data': 'Today\'s Daily Special $7.99 Chicken Fried Rice'}
	elif (counter % 5) == 4:
		data = {'messageTitle': 'Daily Special', "restaurant": 'Sammy\'s Student Exchange', 'data': 'Today is closed'}
	
	# Plaintext request
	#reg_id = 'XXXXXXXXXXXXX'
	#gcm.plaintext_request(registration_id=reg_id, data=data)
	
	print device_token.values()

	# JSON request
	response = gcm.json_request(registration_ids=device_token.values(), data=data)

	counter = counter+1
	data = {}
	data["status"] = "0"
	return json.dumps(data)

	# Extra arguments
	#res = gcm.json_request(registration_ids=reg_ids, data=data, collapse_key='uptoyou', delay_while_idle=True, time_to_live=3600)

# #######################################################

# Connect to the database
conn = sqlite3.connect('restaurant.sqlite')
cursor = conn.cursor()

# Test to see if the server program works
@route('/test')
def echotest():
	test = ["Test successful"]
	json.dumps(test)

# ############### ADMIN CLIENT API's ############### #

# TODO:
# Complete push message API

# Register a new admin to the hub
@post('/register')
def register():
	newID = 0
	user = request.forms.get("user")
	password = request.forms.get("password")
	placeName = request.forms.get("placeName")
	buildingName = request.forms.get("buildingName")
	longitude = request.forms.get("longitude")
	latitude = request.forms.get("latitude")
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = {}

	# 1. Create the login entry for the new admin user
	# Check if the username or password already exists
	cursor.execute("SELECT * FROM loginCredentials WHERE user = ? OR password = ?", (user,password,))
	
	isUser = cursor.fetchall()
	
	if isUser != None: # User already exists; do not create new account and new food place
		ack["result"] = 1
		return json.dumps(ack)
		
	# Insert the user's login credentials into the database in order to register the user
	cursor.execute("INSERT INTO loginCredentials VALUES(?,?)", (user,password,))
	
	# 2. Create the new food place entries in the database
	
	# Check if a food place already exists
	cursor.execute("SELECT * FROM restaurant WHERE restaurantName = ?", (placeName,))
	
	isPlace = cursor.fetchall()
	
	if isPlace != None: # Food place w/ same name already exists; do not create new food place
		ack["result"] = 1
		return json.dumps(ack)
		
	cursor.execute("SELECT max(restaurantID) FROM restaurant")
	maxID = cursor.fetchone()
	if maxID != None:
		newID = maxID[0] + 1
	
	cursor.execute("INSERT INTO restaurant VALUES(?,?,?,?,?)", (newID,placeName,buildingName,longitude,latitude,))
	
	# Commit the changes to the database
	conn.commit()
	
	# If this point is reached, everything is done successfully
	ack["result"] = 0
	ack["placeID"] = newID
	
	return json.dumps(ack)

# Log in an admin to the hub
@post('/login')
def login():
	user_email = request.forms.get("user_email")
	password = request.forms.get("password")
	
	#Search for the user with the specified password
	cursor.execute("SELECT * FROM loginCredentials WHERE user = ? AND password = ?", (user_email,password,))
	check = cursor.fetchone()
	
	# Set up a JSON object to store return values
	#  0: success
	#  non-zero value: failure
	ack = {}
	
	if check == None: # Login was unsuccessful
		ack["result"] = 1
	else: # Login was successful
		ack["result"] = 0
	
	return json.dumps(ack)
	
@post('/addDetails')
def addDetails():
	placeID = request.forms.get("placeID")
	description = request.forms.get("description")
	cuisineType = request.forms.get("cuisineType")
	hoursOfOperation = request.forms.get("hoursOfOperation")
	phoneNum = request.forms.get("phoneNum")
	image = request.forms.get("image")
	
	# Add the description for the given food place into the database
	cursor.execute("INSERT INTO restaurantDetails VALUES(?,?,?,?,?,?)", (placeID, description, cuisineType, hoursOfOperation, phoneNum, image,))
	
	# Commit the changes to the database
	conn.commit()
	
	# Set up a JSON objet to store return values
	#  0: success
	#  non-zero: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)
	
@post('/updateDescription')
def updateDescription():
	placeID = request.forms.get("placeID")
	description = request.forms.get("description")

	#Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET description = ? WHERE restaurantID = ?", (description, placeID))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)

@post('/updateCuisineType')
def updateCuisineType():
	placeID = request.forms.get("placeID")
	cuisineType = request.forms.get("cuisineType")
	
	#Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET cuisineType = ? WHERE restaurantID = ?", (cuisineType, plaecID))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)

@post('/updateHoursOfOperation')
def updateHoursOfOperation():
	placeID = request.forms.get("placeID")
	hoursOfOperation = request.forms.get("hoursOfOperation")
	
	#Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET hoursOfOperation = ? WHERE restaurantID = ?", (hoursOfOperation, placeID))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)

@post('/updatePhoneNum')
def updatePhoneNum():
	placeID = request.forms.get("placeID")
	phoneNum = request.forms.get("phoneNum")
	
	#Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET phoneNum = ? WHERE restaurantID = ?", (phoneNum, placeID))
	
	#Commit the changes to the database
	conn.commit()
	
	#Set up a JSON objet to store return values
	# 0: success
	# non-zero: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)

@post('/updateImage')
def updateImage():
	placeID = request.forms.get("placeID")
	image = request.forms.get("image")
	
	# Add the description for the given food place into the database
	cursor.execute("UPDATE restaurantDetails SET image = ? WHERE restaurantID = ?", (image, placeID))
	
	# Commit the changes to the database
	conn.commit()
	
	# Set up a JSON objet to store return values
	#  0: success
	#  non-zero: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)
	
@post('/addMenuItem')
def addMenuItem():
	placeID = request.forms.get("placeID")
	itemName = request.forms.get("itemName")
	itemPrice = request.forms.get("itemPrice")
	categoryID = 0
	
	# Set up a JSON objet to store return values
	#  0: success
	#  non-zero: failure
	ack = {}
	
	# Check if the menu item already exists
	cursor.execute("SELECT * FROM menu WHERE restaurantID = ? AND itemName = ?", (placeID, itemName,))
	
	isItem = cursor.fetchall()
	
	if isItem != None:
		ack["result"] = 1
		return json.dumps(ack)
		
	# Add the new menu item into the database
	newID = 0
	
	cursor.execute("SELECT max(itemID) FROM menu WHERE restaurantID = ?", (placeID,))
	maxID = cursor.fetchone()
	
	if maxID != None:
		newID = maxID[0] + 1
		
	cursor.execute("INSERT INTO menu VALUES(?,?,?,?,?)", (placeID, newID, itemName, itemPrice, categoryID,))
	
	# Commit the changes to the database
	conn.commit()
	
	# If this point is reached, everything was done successfully
	ack["result"] = 0
	ack["itemID"] = newID
	
	return json.dumps(ack)
	
@post('/updateMenuItemName')
def updateMenuItemName():
	placeID = request.forms.get("placeID")
	itemID = request.forms.get("itemID")
	itemName = request.forms.get("itemName")
	
	cursor.execute("UPDATE menu SET itemName = ? WHERE restaurantID = ? AND itemID = ?", (itemName, placeID, itemID,))
	
	conn.commit()
	
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)
	
@post('/updateMenuItemPrice')
def updateMenuItemName():
	placeID = request.forms.get("placeID")
	itemID = request.forms.get("itemID")
	itemName = request.forms.get("itemPrice")
	
	cursor.execute("UPDATE menu SET price = ? WHERE restaurantID = ? AND itemID = ?", (itemPrice, placeID, itemID,))
	
	conn.commit()
	
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)
	
@post('/deleteMenuItem')
def deleteMenuItem():
	placeID = request.forms.get("placeID")
	itemID = request.forms.get("itemID")
	
	cursor.execute("DELETE FROM menu WHERE restaurantID = ? AND itemID = ?", (placeID, itemID,))
	
	conn.commit()
	
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)

@post('/pushMessage')
def pushMessage():
	global device_token
	placeID = request.forms.get("placeID")
	message = request.forms.get("message")
	
	# Set up a JSON object with a return value
	# 0: success
	# non-zero value: failure
	ack = {}
	
	# Retrieve all of the users for a certain food place
	cursor.execute("SELECT userEmail FROM subscription WHERE restaurantID = ?", (placeID,))
	
	users = cursor.fetchall()
	
	if users == None:
		ack["result"] = 1
		return json.dumps(ack)
	
	subs_tokens = {}
	
	for sub in users:
		subs_tokens[sub[0]] = device_token[sub[0]]
	
	response = gcm.json_request(registration_ids=subs_tokens.values(), data=message)
	
	ack["result"] = 0
	
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
		data.append({"itemID": row[1], "itemName": row[2], "price": row[3]})
	
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
		data.append({"placeID": row[0], "restaurant": row[1], "building": row[2], "Longitude": row[3], "Latitude": row[4]})

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
	
	data = {}
	
	for row in cursor:
		data["description"] = row[1]
		data["cuisineType"] = row[2]
		data["hoursOfOperation"] = row[3]
		data["phoneNum"] = row[4]
		#data["images"] = row[5]
		
	return json.dumps(data)
	
# Get the review and rating for a given food place
@post('/getReviews')
def reviewRating():
	
	placeID = request.forms.get("placeID")
	index = request.forms.get("index")

	# Find the largest review ID for the given food place
	cursor.execute("SELECT max(reviewID) FROM review WHERE restaurantID = ?", (placeID,))
	entry = cursor.fetchone()
	if entry != None:
		maxReviewID = entry[0]
	
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
	placeID = request.forms.get("placeID")
	rating = request.forms.get("rating")
	comments = request.forms.get("comments")
	submitBy = request.forms.get("submitBy")
	
	# Find the largest review ID for the given food place
	cursor.execute("SELECT max(reviewID) FROM review WHERE restaurantID = ?", (placeID,))
	if cursor != None:
		maxID = cursor.fetchone()
		if maxID[0] != None:
			newID = maxID[0] + 1
		else:
			newID = 1
	
	# Get the current timestamp
	current_time = datetime.now().strftime("%Y/%m/%d %I:%M%p")
	
	#Insert a review and rating for a given food place from a given user
	cursor.execute("INSERT INTO review VALUES(?,?,?,?,?,?)", (placeID,newID,comments,rating,current_time,submitBy,))
	
	#Commit the changes to the database
	conn.commit()
	
	# Set up a JSON object with a return value
	# 0: success
	# non-zero value: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)
	
@post('/addSubscription')
def addSubscription():
	placeID = request.forms.get("placeID")
	user_email = request.forms.get("user_email")
	
	# Set up a JSON object with a return value
	# 0: success
	# non-zero value: failure
	ack = {}
	
	try:
		cursor.execute("INSERT INTO subscription VALUES(?,?)", (user_email,placeID,))
		conn.commit()
	except sqlite3.IntegrityError:
		conn.rollback()
		ack["result"] = 1
		return json.dumps(ack)

	ack["result"] = 0		
	return json.dumps(ack)
	
@post('/removeSubscription')
def removeSubscription():
	user_email = request.forms.get("user_email")
	placeID = request.forms.get("placeID")
	
	#Delete the entry containing the user and the device ID associated with that user
	cursor.execute("DELETE FROM subscription WHERE userEmail = ? AND restaurantID = ?", (user_email,placeID,))
	
	#Commit the changes to the database
	conn.commit()
	
	# Set up a JSON object with a return value
	# 0: success
	# non-zero value: failure
	ack = {}
	ack["result"] = 0
	
	return json.dumps(ack)

# #####################OAuth Functions######################## #
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
# ############################################################ #


run(host = "192.168.0.109", port = 8080)
conn.close()