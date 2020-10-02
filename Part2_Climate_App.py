#Dependiences 
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct, and_
from flask import Flask, jsonify

##########################################################
#Database Setup
##########################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement= Base.classes.measurement 
station= Base.classes.station

# Create our session (link) from Python to the DB
session= Session(engine)

#########################################################
#Flask Setup
########################################################
app = Flask(__name__)

#########################################################
# Flask Routes
#########################################################

# Applicaitons pages 
@app.route("/")
def home():
    """Homepage to list all available api routes."""
    return (
        "Welcome to the Climate App homepage below are the pages available!<br/>"
        f"Precipation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature Observations: /api/v1.0/tobs<br/>"
        f"For Minimum Temperature, Avg Temperature, Max Temperature <br/>"
            "enter the dates <YYYY-MM-DD> after /api/v1.0/<start> or /api/v1.0/<start>/<end>"
        )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query the precippitation data from 1 year ago and return a dictionary"""
    # Session (link) from Python to the DB
    session = Session(engine)

    # Query 12 month precipitation data
    tweleve = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >'2016-08-22').all()

    session.close()

    # Creating precipitation dictionary for api 
    tweleve_yr_precip = []
    for date, prcp in tweleve:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        tweleve_yr_precip.append(precip_dict)

    return jsonify(tweleve_yr_precip)

@app.route("/api/v1.0/stations")
def stations():
    """Query the station number and name"""
    #Session (link) from Python to the DB
    session = Session(engine)

    #Query station information
    hi_weather_st = session.query(station.station, station.name).all()

    session.close()

    #Creating station dictionary for api
    weather_stations = []
    for station_code, name in hi_weather_st:
        station_dict = {}
        station_dict["station_code"]= station_code
        station_dict["name"]= name
        weather_stations.append(station_dict)
    
    return jsonify(weather_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations for most active station"""
    #Session from Python to the DB
    session = Session(engine)

    #Query station information
    waihee_obs = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >'2016-08-22').\
        filter(measurement.station == 'USC00519281').all()
    
    #Creating a dictionary for api temp/obs of Wahiee
    wahiee = []
    for date, obs in waihee_obs:
        wahiee_dict = {}
        wahiee_dict["date"] = date
        wahiee_dict["obs"] = obs
        wahiee.append(wahiee_dict)
    return jsonify(wahiee) 

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Function/Query to obtain the temperature obs (min,avg,max) of dates inputed by user"""
    
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    
    if not end:
        results = session.query(*sel).\
            filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    else:
        results = session.query(*sel).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
    
if __name__ == "__main__":
    app.run(debug=True)
