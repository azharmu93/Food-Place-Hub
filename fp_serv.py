from bottle import route, run, request, template, redirect, error, static_file, get, response
import bottle
import json
import sqlite3

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

run(host = "localhost", port = 8080)

conn.close()