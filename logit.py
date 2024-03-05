import time
import waterdb

def logit(msg, valve):

	if (valve > 0):
		print("%s Valve %d - %s" % (time.ctime(time.time()), valve, msg))
	else:
		print("System Message: 	%s %s" % (time.ctime(time.time()), msg))

	try:
		wdb = waterdb.waterdb()
		#     print "logit valve = " + str(valve)
		#     print "logit msg = " + msg
		wdb.addHistory(valve, msg)

	except Exception as error:
		print(error)
		print("%s %s" % (time.ctime(time.time()), msg))
		print("Failed to add history")
        

