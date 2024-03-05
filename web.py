from flask import Flask
from flask import jsonify
from flask import render_template
from flask import Blueprint
from flask import request
# from jinja2.ext import debug

import water
import waterdb
import atexit
import signal
import sys
import time
import logit

bp = Blueprint("watering", __name__, template_folder="templates", static_folder="static")

app = Flask(__name__)

VALVE  = []
THREAD = []

# Note that all the paths here are using the "Blueprint" object, and are prefixed with url_prefix, set further below.
# This allows us to proxy through an internet facing host instead of having to open the Raspberry Pi to the internet. 

    #@app.route("/")
@bp.route("/")
def hello():
    wdb = waterdb.waterdb()
    return render_template("status.html", valves = wdb.ValveState(THREAD))

@bp.route("/gethistory")
def hist():
    wdb = waterdb.waterdb()
    return render_template("history.html", history = wdb.getHistory())



@bp.route("/schedule")
def schedule():
    wdb = waterdb.waterdb()
    return render_template("schedule.html", timers = wdb.getAllTimers())



@bp.route("/edit")
def edit():
    get_vars = dict( 
            day       = request.args.get('day'),
            start     = request.args.get('start'),
            valve     = request.args.get('valve'),
            duration  = request.args.get('duration'),
            dayn      = request.args.get("dayn"),
            mode      = "edit")

    wdb = waterdb.waterdb()
 
    names = wdb.getValveNames()

    return render_template("edit.html", form = get_vars, valvenames  = names)



@bp.route("/insert")
def insert():
    get_vars = dict( 
            day       = "0",
            start     = "07:00:00",
            valve     = "1",
            duration  = "00:05:00",
            mode      = "insert")

    wdb = waterdb.waterdb()
 
    names = wdb.getValveNames()

    return render_template("edit.html", form = get_vars, valvenames  = names)



@bp.route("/inssched", methods=['POST'])
def insertSchedule():

    reqData = request.get_json()

    wdb = waterdb.waterdb()
 
    wdb.insertSchedule(reqData['valve'], reqData['start'], reqData['duration'], reqData['dayn'])
    
    days = { 0 : "All Days",
             1 : "Monday",
             2 : "Tuesday",
             3 : "Wednesday",
             4 : "Thursday",
             5 : "Friday",
             6 : "Saturday",
             7 : "Sunday" }
    
    logit.logit("Schedule inserted to start at " + reqData['start'] + " for " + reqData['duration'] + " on " + days[reqData['dayn']], wdb.getPin(reqData['valve']))
    return "OK"



@bp.route("/updsched", methods=['POST'])
def updateSchedule():

    reqData = request.get_json()

    wdb = waterdb.waterdb()
 
    wdb.updateSchedule(reqData['valve'], reqData['start'], reqData['duration'], reqData['dayn'], reqData['oldstart'], reqData['oldduration'], reqData['olddayn'])
    
    days = { 0 : "All Days",
             1 : "Monday",
             2 : "Tuesday",
             3 : "Wednesday",
             4 : "Thursday",
             5 : "Friday",
             6 : "Saturday",
             7 : "Sunday" }
    
    print(reqData['dayn'], reqData['olddayn'])
    print(days[0])
    print(days[reqData['olddayn'] + 1])
    
    logit.logit("Schedule updated to " + reqData['start'] + " for " + reqData['duration'] + " on " + days[reqData['dayn']] + "; was at " + reqData['oldstart'] + " for " + reqData['oldduration'] + " on " + days[reqData['olddayn']] + ".", wdb.getPin(reqData['valve']))
    return "OK"



@bp.route("/delsched", methods=['POST'])
def deleteSchedule():

    reqData = request.get_json()

    wdb = waterdb.waterdb()
 
    wdb.deleteSchedule(reqData['valve'], reqData['start'], reqData['duration'], reqData['dayn'])
    
    logit.logit("Schedule starting at " + reqData['start'] + " for " + reqData['duration'] + " on " + reqData['day'] + " deleted.", wdb.getPin(reqData['valve']))

    return "OK"



@bp.route("/von/<valve>", methods=['POST'])
def on(valve):
    try:
        vint = int(valve)
    except ValueError:
        return "Invalid Valve!"
    else:
        if (vint < 1 or vint > 4): 
            return "Value out of range"
            return 0

        logit.logit("Manual start", THREAD[vint - 1].getValve())

        THREAD[vint - 1].openValve(300)
        
#        print "Vint = " + str(vint)

    l = THREAD[vint - 1].remaining()

    if (l["left"] > 0):
        return ("%02.0d:%02.0d:%02.0d remaining (ending %s)" % (l["left"]//3600, l["left"]//60, int(l["left"]%60), l["endtime"].ctime()))
    else:
        return ""
        
        
@bp.route("/voff/<valve>", methods=['POST'])
def off(valve):
    try:
        vint = int(valve)
    except ValueError:
        return "Invalid Valve!"
    else:
        if (vint < 1 or vint > 4): 
            return "Value out of range"

    logit.logit("Manual stop", THREAD[vint - 1].getValve())

    THREAD[vint - 1].closeValve()

    #        print "Vint = " + str(vint)

    return ("Valve %d closed.") % (vint)


@bp.route("/editname", methods=['POST'])
def editname():
    
    reqData = request.get_json()

    wdb = waterdb.waterdb()
 
    wdb.updateValveName(reqData['valve'], reqData['newName'])
    
    logit.logit("Valve " + str(reqData['valve']) + " name updated to " + reqData['newName'], 0)

    return "OK"




@bp.route("/timer/<valve>")
def timer(valve):
    try:
        vint = int(valve)
    except ValueError:
        return "Invalid Valve!"
    else:
        if (vint < 1 or vint > 4): 
            return "Value out of range"
            return 0
        wdb = waterdb.waterdb()	
        wdb.getTimer(vint)
    
        return "Done"


@bp.route("/vstate", methods=['GET'])
def vstate():

        wdb = waterdb.waterdb()
    
        return jsonify(wdb.ValveState(THREAD))


@bp.route("/alloff", methods=['GET'])
def alloff():

        for n,v in enumerate(THREAD):
            v.closeValve()
            
        return "All valves closed."




def signal_handler(signal, frame):

        for n,v in enumerate(THREAD):
            v.stop()
            v.join()
    
        logit.logit("System Shutdown", 0)
    
        sys.exit(0)
    
# This prefixes all the paths with /watering to allow proxying. 

app.register_blueprint(bp, url_prefix="/watering")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    logit.logit("System Startup", 0)
    
    wdb = waterdb.waterdb()
    
    valves = wdb.getValves()
    
    for v in valves:
        t = water.valveThread(v["pin"], v["valve"])
        t.start()
        THREAD.append(t)

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host='0.0.0.0', port=8215, threaded=True)

