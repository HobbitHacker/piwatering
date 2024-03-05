#!/usr/bin/python

import MySQLdb
import MySQLdb.cursors
import dbconfig

db = MySQLdb.connect(dbconfig.host, dbconfig.user, dbconfig.password, dbconfig.dbname, cursorclass=MySQLdb.cursors.DictCursor)

cursor = db.cursor()

cursor.execute("SELECT valve,name FROM valves")

allvalves = cursor.fetchall()

for valve in allvalves:
	print("Valve %d - %s" % (valve["valve"], valve["name"]))

db.close()
