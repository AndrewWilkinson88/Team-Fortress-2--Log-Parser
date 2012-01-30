#The different classes to represent the different tables

import re
import os
import time
import sqlite3
###
### This class defines a player connecting to the server
### 4 variabls
###
class Connection:
	def __init__(self):
		self.timestamp = ''
		self.playerID = ''
		self.playerName = ''
		self.playerIP = ''
	
	def write(self, cursor, mapName, date_key):
		playerName = self.playerName.decode("UTF-8")
		t = ( mapName, date_key, self.timestamp, self.playerID, playerName, self.playerIP )
		cursor.execute( unicode('INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?)'), t ) 

###
### This class defines a player disconnecting from the server. 
### 2 variables
###
class Disconnection:
	def __init__(self):
		self.timestamp = ''
		self.playerID = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.playerID )
		cursor.execute( 'INSERT INTO disconnections VALUES (?, ?, ?, ?)', t ) 

###
###	This class defines when a player changes teams. Tracks KAD to see if there's a 
### correlation. 4 variables
###
class TeamChange:
	def __init__(self):
		self.timestamp = ''
		self.playerID = ''
		self.toTeam = ''
		self.fromTeam = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.playerID, self.toTeam, self.fromTeam )
		cursor.execute( 'INSERT INTO teamChanges VALUES (?, ?, ?, ?, ?, ?)', t ) 

###
###	This class defines when a player changes roles.
### 4 variables
###
class RoleChange:
	def __init__(self):
		self.timestamp = ''
		self.playerID = ''
		self.toRole = ''
		self.fromRole = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.playerID, self.toRole, self.fromRole )
		cursor.execute( 'INSERT INTO roleChanges VALUES (?, ?, ?, ?, ?, ?)', t ) 

###
### This class defines a Kill which contains information about the killer, the assister,
### and the victim. 12 variables
###
class Kill:
	def __init__(self):
		self.timestamp = ''
		self.customKill = ''
		self.killerWeapon = ''
		self.killerID = ''
		self.killerRole = ''
		self.killerPosition = ''
		self.assisterID = ''
		self.assisterRole = ''
		self.assisterPosition = ''
		self.victimID = ''
		self.victimRole = ''
		self.victimPosition = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.customKill, self.killerWeapon, self.killerID, self.killerRole, self.killerPosition, self.assisterID, self.assisterRole, self.assisterPosition, self.victimID, self.victimRole, self.victimPosition )
		cursor.execute( 'INSERT INTO kills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', t ) 

###
### This class defines an object Built (i.e. sentryGun, teleporter...)
###	4 variables
###
class ObjBuilt:
	def __init__(self):
		self.timestamp = ''
		self.ownerID = ''
		self.objectType = ''
		self.objectPosition = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.ownerID, self.objectType, self.objectPosition )
		cursor.execute( 'INSERT INTO builtObjects VALUES (?, ?, ?, ?, ?, ?)', t )

###
### This class defines an object Destroyed (i.e. sentryGun, teleporter...)
### 9 variables
###
class ObjDestroyed:
	def __init__(self):
		self.timestamp = ''
		self.timeLasted = 0		
		self.killerWeapon = ''
		self.killerID = ''
		self.killerRole = ''
		self.killerPosition = ''
		self.ownerID = ''
		self.objectType = ''
		self.objectPosition = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.timeLasted, self.killerWeapon, self.killerID, self.killerRole, self.killerPosition, self.ownerID, self.objectType, self.objectPosition )
		cursor.execute( 'INSERT INTO destroyedObjects VALUES (?,?,?,?,?,?,?,?,?,?,?)', t )
		
###
### This class defines when a player Defends a point
### 3 variables
###
class PointDefend:
	def __init__(self):
		self.timestamp = ''
		self.pointName = ''		
		self.playerID = ''
		self.playerRole = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.pointName, self.playerID, self.playerRole )
		cursor.execute( 'INSERT INTO pointDefends VALUES (?, ?, ?, ?, ?, ?)', t )

###
### This class defines when a player captures a point normally grouped
### together all at once, but will seereate into different entries. 
### 3 variables
###
class PointCapture:
	def __init__(self):
		self.timestamp = ''
		self.pointName = ''
		self.playerID = ''
		self.playerRole = ''

	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.timestamp, self.pointName, self.playerID, self.playerRole )
		cursor.execute( 'INSERT INTO pointCaptures VALUES (?, ?, ?, ?, ?, ?)', t )

###
### This class defines when a round/miniRound Win occurs on the given map instance.
### 
class Wins:
	def __init__(self):
		self.roundBegin = ''
		self.roundEnd = ''
		self.teamWon = ''
	
	def write(self, cursor, mapName, date_key):
		t = (mapName, date_key, self.roundBegin, self.roundEnd, self.teamWon )
		cursor.execute( 'INSERT INTO pointDefends VALUES (?, ?, ?, ?, ?)', t )

###
### This class defines a player object, to retain role, and team.
###
class Player:
	def __init__(self):		
		self.playerID = ''	
		self.currRole = 'Unassigned'
		self.team = 'Unassigned'
		self.objects = dict()

class Object:
	def __init__(self):
		self.position = ''
		self.timestamp = ''
