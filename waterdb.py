#!/usr/bin/python

import pymysql.cursors
import datetime
import dbconfig

class waterdb:
        "Database interface for Watering System"

        def fetch(self, sql):
                
                self.conn()

                cursor = self.wdb.cursor()

                cursor.execute(sql)

                return cursor.fetchall()



        def conn(self):
                
                self.wdb = pymysql.connect(host=dbconfig.host, user=dbconfig.user, password=dbconfig.password, database=dbconfig.dbname, cursorclass=pymysql.cursors.DictCursor)                


                
        def disc(self):

                self.wdb.close()

            

        def ValveState(self, THREAD):
                v = [] 

                allvalves = self.fetch("SELECT valve,name FROM valves")

                for valve in allvalves:

                        l = THREAD[valve["valve"] - 1].remaining()

                        if (l["left"] > 0):
                            ltxt = ("%02.0d:%02.0d:%02.0d remaining (ending %s)" % (l["left"]//3600, l["left"]//60, int(l["left"]%60), l["endtime"].ctime()))
                        else:
                            ltxt = ""

                        v.append({"valve" : valve["valve"],
                                  "name" : valve["name"], 
                                  "status" : THREAD[valve["valve"] - 1].getState(),
                                  "left":  ltxt})
                        
                self.disc()		

                return v


            
        def getTimer(self, valve):
        
                now = datetime.datetime.now()
                window = now + datetime.timedelta(seconds=300)
                dow = now.isoweekday()

                alltimers = self.fetch(sql = "select time_to_sec(timediff(watering.end(start,duration),now())) as remaining " \
                            "from timers a, valves b " \
                            "where a.start < now() " \
                                  "and watering.end(a.start, a.duration) > now() " \
                                  "and b.pin = %d " \
                                  "and a.valve = b.valve " \
                                  "and a.day in(0,%d)" \
                                  % (valve, dow))

#                sql = "SELECT a.valve, a.start, a.duration " \
#                                 "FROM timers a, valves b " \
#                                 "WHERE a.valve = b.valve AND a.start >= '%s' AND a.start <= '%s' AND a.day IN(0,%d) " \
#                                 "AND b.pin = %d" % (now.strftime("%H:%M:%S"), window.strftime("%H:%M:%S"), dow, valve)
                
                t = []
                
 #               if (cursor.rowcount > 0):
 #                   print "Found " + str(cursor.rowcount) + " rows"
                
                for onetime in alltimers:
                        t.append({"remaining" : onetime["remaining"]})
#                        print "Pin: " + str(valve) + " Remaining: " + str(onetime["remaining"])
                        
                self.disc()
                
                return t



        def getTimers(self, valve):
        
                alltimers = self.fetch(sql = "select a.start, a.duration, a.day, false as done " \
                                  "from timers a, valves b " \
                                  "where b.pin = %d " \
                                  "and a.valve = b.valve " \
                                  % (valve))

#                sql = "SELECT a.valve, a.start, a.duration " \
#                                 "FROM timers a, valves b " \
#                                 "WHERE a.valve = b.valve AND a.start >= '%s' AND a.start <= '%s' AND a.day IN(0,%d) " \
#                                 "AND b.pin = %d" % (now.strftime("%H:%M:%S"), window.strftime("%H:%M:%S"), dow, valve)
                
#                t = []
                
 #               if (cursor.rowcount > 0):
 #                   print "Found " + str(cursor.rowcount) + " rows"
                
#                for onetime in alltimers:

#                        t.append({"start" : onetime["start"],  \
#                                  "duration" : onetime["duration"], \
#                                  "day": onetime["day"]})

#                        print "Pin: " + str(valve) + " Remaining: " + str(onetime["remaining"])
                        
                self.disc()
                
                return alltimers
            
            
            
        def getAllTimers(self):
        
                now = datetime.datetime.now()
                window = now + datetime.timedelta(seconds=300)
                dow = now.isoweekday()

                alltimers = self.fetch("select a.valve, a.start, a.duration, a.day, b.name " \
                             "from timers a, valves b " \
                             "where a.valve = b.valve " \
                             "order by a.day, a.start, a.valve")
                
                t = []
                
 #               if (cursor.rowcount > 0):
 #                   print "Found " + str(cursor.rowcount) + " rows"
                
                days = {"Mon","Tue","Wed","Thu","Fri","Sat","Sun"}
                
                for onetime in alltimers:
                    
                        if onetime["day"] == 0:
                            day = "All Days"
                        else:
                            day = days[onetime["day"]]
                            
                        t.append({"day"      : day,
                                  "dayn"     : onetime["day"],
                                  "start"    : onetime["start"],
                                  "valve"    : onetime["valve"],
                                  "name"     : onetime["name"],
                                  "duration" : onetime["duration"]})
                        
#                        print onetime
                        
                self.disc()
                
                return t
            
            
            
        def addHistory(self, valve, text):
            
                now = datetime.datetime.now()
            
                wdb = pymysql.connect(host=dbconfig.host, user=dbconfig.user, password=dbconfig.password, db=dbconfig.dbname, cursorclass=pymysql.cursors.DictCursor)                
            
                cursor = wdb.cursor()
            
                v = {}

#            print "valve = " + str(valve)
            
                if (valve > 0):
                        cursor.execute("select valve from valves where pin = %d" % (valve))
                        v = cursor.fetchone()
                else:
                        v["valve"] = 0
                
#                print "V = " + str(v)
            
                cursor.execute("insert into history set valve = %d, ts = '%s', message = '%s'" % (v["valve"], now.isoformat(), text))
            
                wdb.commit()
            
                wdb.close()
            
            
            
        def getValves(self):
        
                allvalves = self.fetch("SELECT valve,pin FROM valves")
		
                self.disc()
		
                return allvalves



        def getPin(self, valve):
        
                pin = self.fetch("SELECT pin FROM valves WHERE valve = %d" % (valve))
		
                self.disc()
		
                return pin[0]['pin']



        def getValveNames(self):

                allValveNames = self.fetch("SELECT valve, name from valves")

                self.disc()

                return allValveNames



        def updateValveName(self, valve, newName):
                            
                self.conn()
                
                cursor = self.wdb.cursor()
                        
                cursor.execute("update valves set name = '%s' where valve = %d" % (newName, valve))
                
                self.wdb.commit()
                
                self.disc()

                return ""




        def insertSchedule(self, valve, newstart, newduration, newday):

                self.conn()
                
                cursor = self.wdb.cursor()
                        
                cursor.execute("insert into timers values(%d, '%s', '%s', %d)" % (valve, newstart, newduration, newday))
                
                self.wdb.commit()
                
                self.disc()

                return ""



        def deleteSchedule(self, valve, start, duration, daynum):
                        
                self.conn()
        
                cursor = self.wdb.cursor()
                
                cursor.execute("delete from timers where valve = %d and start = '%s' and duration = '%s' and day = %d" % (valve, start, duration, daynum))
        
                self.wdb.commit()
                
                self.disc()

                return ""
                


        def updateSchedule(self, valve, newstart, newduration, newday, oldstart, oldduration, oldday):

                self.conn()
                
                cursor = self.wdb.cursor()
                        
                cursor.execute("update timers set start = '%s', duration = '%s', day = %d " \
                                        "where valve = %d " \
                                        "and start = '%s' " \
                                        "and duration = '%s' "\
                                        "and day = %d" % (newstart, newduration, newday, valve, oldstart, oldduration, oldday))
                self.wdb.commit()
                
                self.disc()

                return ""

                
                
        def getHistory(self):
        
                hist = self.fetch("select a.valve, b.name, a.message, a.ts " \
                                  "from history a " \
                                  "left join valves b on a.valve = b.valve " \
                                  "order by a.ts desc, a.valve " \
                                  "limit 50")
                
                self.disc()
                
                return hist
