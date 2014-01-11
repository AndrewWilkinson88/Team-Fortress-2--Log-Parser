#!/usr/bin/python
import re
import os
import time
import sqlite3
import LogTypes

###	
###	This class is set up to process a single .log file, and create new files
### containing map instance data, such as player data, class data, and general
### map info. 
###
class Process:

	def initTables( self ):
			self.cursor.execute( 'CREATE TABLE connections( map text, date_key text, timestamp text, playerID text, playerName text, playerIP text) ' )
			self.cursor.execute( 'CREATE TABLE disconnections( map text, date_key text, timestamp text, playerID text) ' )
			self.cursor.execute( 'CREATE TABLE teamChanges( map text, date_key text, timestamp text, playerID text, toTeam text, fromTeam text) ' )
			self.cursor.execute( 'CREATE TABLE roleChanges( map text, date_key text, timestamp text, playerID text, toRole text, fromRole text) ' )
			self.cursor.execute( 'CREATE TABLE kills( map text, date_key text, timestamp text, customKill text, killerWeapon text, killerID text, killerRole text, killerPosition text, assisterID text, assisterRole text, assisterPosition text, victimID text, victimRole text, victimPosition text) ' )
			self.cursor.execute( 'CREATE TABLE builtObjects( map text, date_key text, timestamp text, playerID text, objectBuilt text, objectPosition text) ' )
			self.cursor.execute( 'CREATE TABLE destroyedObjects( map text, date_key text, timestamp text, timelasted float, killerWeapon text, killerID text, killerRole text, killerPosition text, ownerID text, objectDestroyed text, objectPosition text) ' )
			self.cursor.execute( 'CREATE TABLE pointDefends( map text, date_key text, timestamp text, pointName text, playerID text, playerRole text) ' )
			self.cursor.execute( 'CREATE TABLE pointCaptures( map text, date_key text, timestamp text, pointName text, playerID text, playerRole text) ' )
			self.cursor.execute( 'CREATE TABLE wins( map text, date_key text, roundBegin text, roundEnd text, teamWon text) ' )
			
	##Each variable represents a different table in the database
	def __init__(self):
		self.connections = list()
		self.disconnections = list()
		self.teamChanges = list()
		self.roleChanges = list()
		self.kills = list()
		self.builtObjects = list()
		self.destroyedObjects = list()
		self.pointDefends = list()
		self.pointCaptures = list()
		self.wins = list()		
		self.players = dict()
				
		self.date_keys = list()		
		fileName = "10-10-2010.0.log"
		## Variables set per map instance
		self.date_key = fileName[6:10] + '-' + fileName[0:2] + '-' + fileName[3:5] + '_0'
		self.mapKeys = dict()		

		self.valid_map = False
		self.database = 'tf2Stats'
		self.directory = '/home/awilkins/Desktop/School/Data Vis/Vis Work/Test/'
		self.connection = sqlite3.connect( self.directory + self.database )
		self.cursor = self.connection.cursor()
		try:
			self.initTables()
		except:
			print "All tables Exist"
		self.curr_map = 'null'
		self.processFile( './10-10-2010.0.log' )
	
	def reset(self):
		self.connections = list()
		self.disconnections = list()
		self.teamChanges = list()
		self.roleChanges = list()
		self.kills = list()
		self.builtObjects = list()
		self.destroyedObjects = list()
		self.pointDefends = list()
		self.pointCaptures = list()
		self.wins = list()		

	##Player connected
	##parse out timeStamp/name/ID/IP	
	def playerConnected( self, line ):
		time_connected = line[15:23]
		line = line[25:]
		line = line.split( 'connected, address' )
		name = line[0][1:len(line[0])-4]
		IP = line[1][2:len(line[1])-2] #working IP
		name = name.split( '<' )
		ID = name.pop()
		ID = ID[:len(ID)-1]
		name.pop()
		i = 0
		while i < len(name):
			name[i] += '<'
			i += 1
		name = "".join(name)
		name = name[:len(name)-1]

		#add Connection
		newConn = Connection()
		newConn.timestamp = time_connected
		newConn.playerName = name
		newConn.playerID = ID
		newConn.playerIP = IP
		self.connections.append( newConn )
		if not (ID in self.players):
			self.players[ID] = Player()
			self.players[ID].playerID = ID
		
	##Player disconnected
	##parse out timeStamp/ID
	def playerDisconnected( self, line ):

		time_disconnected = line[15:23]
		line = line[25:]
		line = line.split( '\" disconnected ' )
		ID = line[0][1:len(line[0])]
		ID = ID.split( '<' )
		ID.pop()
		ID = ID.pop()
		ID = ID[:len(ID)-1]
		
		#add disconnection
		newDConn = Disconnection()
		newDConn.timestamp = time_disconnected
		newDConn.playerID = ID
		self.disconnections.append( newDConn )
		
	##Player switched teams
	##parse out timestamp/ID/teamJoined
	def playerTeam( self, line ):
		timestamp = line[15:23]		
		temp = line.split( '\"' )
		team = temp[len(temp)-2]
		line = line[25:]
		line = line.split( ' joined team ' )
		ID = line[0][1:len(line[0])-4]
		ID = ID.split( '<' )
		ID.pop()
		ID = ID.pop()
		ID = ID[:len(ID)-1]
		
		#add teamChange
		newTChange = TeamChange()
		newTChange.timestamp = timestamp
		newTChange.playerID = ID
		newTChange.toTeam = team
		newTChange.fromTeam = self.players[ID].team
		self.teamChanges.append( newTChange )
		self.players[ID].team = team
		
	##Player changed role
	##parse out timestamp/playerID/toRole/fromRole
	def playerRole( self, line):
		timestamp = line[15:23]				
		temp = line
		role = line.split( '\"' )
		role = role[len(role)-2]
		line = line[25:]
		line = line.split( ' changed role to ' )
		ID = line[0][1:len(line[0])-4]
		ID = ID.split( '<' )
		ID.pop()
		ID = ID.pop()
		ID = ID[:len(ID)-1]
		
		#add roleChange
		newRChange = RoleChange()
		newRChange.timestamp = timestamp
		newRChange.playerID = ID
		newRChange.toRole = role
		newRChange.fromRole = self.players[ID].currRole
		self.roleChanges.append( newRChange )
		self.players[ID].currRole = role
	
	##Player performed kill
	##parse out timestamp/customKill/killerWeapon/killerID/killerClass
	##killerPosition/victimID/victimClass/victimPosition
	def playerKilledSomething( self, line ):
		timestamp = line[15:23]
		line = line[25:]
		line = line.split( '>\" killed \"' )
		killerID = line[0]
		killerID = killerID.split( '<' )
		killerID.pop()
		killerID = killerID.pop()
		killerID = killerID[:len(killerID)-1]
		line = line.pop()
		line = line.split( '<' )
		pos_weapons = line.pop()
		victimID = line.pop()
		victimID = victimID[:len(victimID)-1]
		pos_weapons = pos_weapons.split( '\"' )
		pos_weapons.pop()
		victimPosition = pos_weapons.pop()
		pos_weapons.pop()
		killerPosition = pos_weapons.pop()
		weapon = pos_weapons[2]
		if(pos_weapons[3] == " (customkill "):
			customkill = pos_weapons[4]
		else:
			customkill = ""
		killerRole = self.players[killerID].currRole
		victimRole = self.players[victimID].currRole

		#add Kill
		newKill = Kill()
		newKill.timestamp = timestamp
		newKill.customKill = customkill
		newKill.killerWeapon = weapon		
		newKill.killerID = killerID
		newKill.killerRole = self.players[killerID].currRole		
		newKill.killerPosition = killerPosition
		newKill.victimID = victimID
		newKill.victimRole = self.players[victimID].currRole
		newKill.victimPosition = victimPosition
		self.kills.append( newKill )

	##Player triggered 'kill assist'
	# parse out timestamp/assisterID/assisterRole/
	# assisterPosition/victimID
	def playerAssisted( self, line ):
		timestamp = line[15:23]
		line = line[25:]
		line = line.split( '>\" triggered \"' )
		assisterID = line[0]
		assisterID = assisterID.split( '<' )
		assisterID.pop()
		assisterID = assisterID.pop()
		assisterID = assisterID[:len(assisterID)-1]
		line = line[1]
		line = line.split( '<' )
		positions = line.pop()
		victimID = line.pop()
		victimID = victimID[:len(victimID)-1]
		positions = positions.split( 'assister_position' )
		positions = positions.pop()
		positions = positions.split('\"')
		assisterPosition = positions[1]
		positions.pop()
		victimPosition = positions.pop()

		# Update kill
		# need to take into account victimID, and timestamp
		for kill in self.kills:
			if kill.victimID == victimID and kill.timestamp == timestamp:
				kill.assisterID = assisterID
				kill.assisterRole = self.players[assisterID].currRole
				kill.assisterPosition = assisterPosition
				break

	##Player triggered 'builtobject
	# parse out timestamp/playerID/objectBuilt/objectPosition
	def playerBuiltObject( self, line ):
		timestamp = line[15:23]
		line = line[25:]
		line = line.split( '>\" triggered \"builtobject" (object \"' )
		obj_position = line.pop()
		obj_position = obj_position.split( '\"' )
		objectBuilt = obj_position[0]
		obj_position.pop()
		objectPosition = obj_position.pop() 
		playerID = line.pop()
		playerID = playerID.split( '<' )
		playerID.pop()
		playerID = playerID.pop()
		playerID = playerID[:len(playerID)-1]

		#add objectBuilt
		newObjBuilt = ObjBuilt()
		newObjBuilt.timestamp = timestamp
		newObjBuilt.ownerID = playerID
		newObjBuilt.objectType = objectBuilt
		newObjBuilt.objectPosition = objectPosition
		self.builtObjects.append( newObjBuilt )

		#add/update object on player class
		if( not (objectBuilt in self.players[playerID].objects) ):
			self.players[playerID].objects[objectBuilt] = Object()	
		self.players[playerID].objects[objectBuilt].position = objectPosition
		self.players[playerID].objects[objectBuilt].timestamp = timestamp

	##Player triggered 'Killedobject'
	# parse out timestamp/timelasted/killerWeapon/killerID/killerRole/
	# killerPosition/ownerID/objectDestroyed/objectPosition
	def playerObjectDestroyed( self, line ):
		timestamp = line[15:23]
		line = line[25:]
		line = line.split( '>\" triggered \"killedobject" (object \"' )
		obj_pos_owner = line.pop()
		obj_pos_owner = obj_pos_owner.split( '\"' )
		objectDestroyed = obj_pos_owner[0]
		weapon = obj_pos_owner[2]
		obj_pos_owner.pop()
		attackerPosition = obj_pos_owner.pop()
		obj_pos_owner.pop()
		ownerID = obj_pos_owner.pop()
		ownerID = ownerID.split( '<' )
		ownerID.pop()
		ownerID = ownerID.pop()
		ownerID = ownerID[:len(ownerID)-1]
		killerID = line[0]
		killerID = killerID.split( '<' )
		killerID.pop()
		killerID = killerID.pop()
		killerID = killerID[:len(killerID)-1]

		#pull old object time, and position
		prevTime = self.players[ownerID].objects[objectDestroyed].timestamp
		objectPosition = self.players[ownerID].objects[objectDestroyed].position
		timeLasted = self.calculateTime(prevTime, timestamp)

		#add Destroyed Object
		newDesObj = ObjDestroyed()
		newDesObj.timestamp = timestamp
		newDesObj.killerID = killerID
		newDesObj.killerRole = self.players[killerID].currRole
		newDesObj.killerWeapon = weapon
		newDesObj.killerPosition = attackerPosition
		newDesObj.timeLasted = timeLasted
		newDesObj.ownerID = ownerID
		newDesObj.objectType = objectDestroyed
		newDesObj.objectPosition = objectPosition
		self.destroyedObjects.append( newDesObj )

	##Player triggered point capture
	# parse timestamp/playerID/playerRole
	def playerCapturedPoint( self, line ):
		timestamp = line[15:23]
		line = line[25:]
		line = line.split( '\" triggered \"pointcaptured\"' )
		line = line.pop()
		line = line.split( '(player1 \"' )
		cpName_num = line[0]
		players = line.pop()
		cpName_num = cpName_num.split('\"')
		cpName_num.pop()
		numCappers = cpName_num.pop()
		cpName_num.pop()
		cpName = cpName_num.pop()

		players = players.split( ') (p' )
		for i in range(int(numCappers)):
			position = players.pop()
			position = position.split( '\"' )
			position.pop()
			position = position.pop()
			playerID = players.pop()
			playerID = playerID.split( '<' )
			playerID.pop()	
			playerID = playerID.pop()
			playerID = playerID[:len(playerID)-1]

			#add new Point capture
			newPCapture = PointCapture()
			newPCapture.timestamp = timestamp
			newPCapture.pointName = cpName
			newPCapture.playerPosition = position
			newPCapture.playerID = playerID
			self.pointCaptures.append( newPCapture )
	
	##Player triggered point Defend
	# parse timestamp/playerID/playerRole
	def playerDefendedPoint( self, line ):
		timestamp = line[15:23]
		line = line[25:]
		line = line.split( '>\" triggered \"captureblocked\"' )
		playerID = line[0]
		playerID = playerID.split( '<' )
		playerID.pop()
		playerID = playerID.pop()
		playerID = playerID[:len(playerID)-1]
		cpName_pos = line.pop()
		cpName_pos = cpName_pos.split( '\"' )
		cpName_pos.pop()
		playerPosition = cpName_pos.pop()
		cpName_pos.pop()
		cpName = cpName_pos.pop()

		#add point Defend
		newPDefend = PointDefend()
		newPDefend.timestamp = timestamp
		newPDefend.pointName = cpName
		newPDefend.playerID = playerID
		newPDefend.playerRole = self.players[playerID].currRole
		self.pointDefends.append( newPDefend ) 
		
	##The round ends and one team won
	# parse roundBegin/roundEnd/teamWon
	def roundEnd( self ):
		print "add stuff here"

	###Used to setup data for new map instance
	#Needs massive rewrite to include writing to SQL instead of
	#Writing to file hierarchy
	def processMap(self, line):
			
		for conn in self.connections:
			conn.write(self.cursor, self.curr_map, self.date_key)
		for disConn in self.disconnections:
			disConn.write(self.cursor, self.curr_map, self.date_key)

		# -- if map is valid begin writing player information to the table
		if(self.valid_map):
			if( self.curr_map in self.mapKeys ):
				self.mapKeys[self.curr_map] += 1
			else:
				self.mapKeys[self.curr_map] = 0
			temp = self.date_key[:len(self.date_key)-1] + str(self.mapKeys[self.curr_map])
			self.date_key = temp

			for tChange in self.teamChanges:
				tChange.write(self.cursor, self.curr_map, self.date_key)
			for rChange in self.roleChanges:
				rChange.write(self.cursor, self.curr_map, self.date_key)
			for kill in self.kills:
				kill.write(self.cursor, self.curr_map, self.date_key)
			for bObject in self.builtObjects:
				bObject.write(self.cursor, self.curr_map, self.date_key)
			for dObject in self.destroyedObjects:
				dObject.write(self.cursor, self.curr_map, self.date_key)
			for pDefend in self.pointDefends:
				pDefend.write(self.cursor, self.curr_map, self.date_key)
			for pCapture in self.pointCaptures:
				pCapture.write(self.cursor, self.curr_map, self.date_key)
			for win in self.wins:
				win.write(self.cursor, self.curr_map, self.date_key)	
			self.connection.commit()

		# -- set the current map to the one being loaded
		self.curr_map = line[38:len(line)-2]
		self.valid_map = True
		self.reset()

	###This function is where the program processes each line
	def processFile(self, file_name):
		work_file = open( file_name, 'r' )
		#i = 0	
		for line in work_file:
			#i += 1
			#print str(i)

			if( re.search(" connected, address",  line ) != None ):
				self.playerConnected(line)
				continue
			
			if( re.search(" disconnected ", line ) != None ):
				self.playerDisconnected(line)
				continue
			
			if( re.search(" Loading map ", line ) != None ):
				self.processMap(line)
				continue
	
			# -- if I don't know what the map is don't bother taking stats
			if not self.valid_map: 
				continue

			if( re.search(" joined team ", line ) != None ):
				self.playerTeam(line)
				continue
			if( re.search(" changed role to ", line ) != None ):
				self.playerRole(line)
				continue
			if( re.search( '>\" killed \"', line ) != None ):
				self.playerKilledSomething(line)
				continue
			if( re.search( 'triggered \"kill assist\"', line ) != None ):
				self.playerAssisted(line)
				continue
			if( re.search( 'triggered \"builtobject\"', line ) != None ):
				self.playerBuiltObject(line)
				continue
			if( re.search( 'triggered \"killedobject\"', line ) != None ):
				if( re.search( 'assist \"', line ) == None ):
					self.playerObjectDestroyed(line)
				continue
			if( re.search( 'triggered \"pointcaptured\"', line ) != None ):
				self.playerCapturedPoint(line)
				continue
			if( re.search( 'triggered \"captureblocked\"', line ) != None ):
				self.playerDefendedPoint(line)
				continue
				

	###Used to calculate the difference between two times
	def calculateTime(self, time1, time2):
		hours   = int(time2[0:2]) - int(time1[0:2])
		if hours < 0 : hours += 24
		minutes = int(time2[3:5]) - int(time1[3:5])
		seconds = int(time2[6:8]) - int(time1[6:8])	
		return hours * 3600 + minutes * 60 + seconds
