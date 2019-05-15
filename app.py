import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "NOTE :  in the following two routes, replace 'start_date' and 'end_date' with the dates you would like to query in yyyy-mm-dd format<br/>"
        "/api/v1.0/start_date<br/>"
        "/api/v1.0/start_date/end_date"
    )
#returns JSON of dictionary containing dates as keys
# and precipitation measurements as values
@app.route("/api/v1.0/precipitation/")
def precipitation ():
    """ returns JSON of dictionary containing dates"""
    """as keys and precipitation measurements as values"""
    results = session.query(Measurement.date, Measurement.prcp).all()
    prcp_list = []
    
    for result in results:
        prcp_dict = {}
        date = result.date
        prcp_dict[f"{date}"]= result.prcp
        prcp_list.append(prcp_dict)
    print (prcp_list)
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def getStations ():
    """ return JSON List of stations from dataset"""
    results = session.query(Measurement.station).group_by(Measurement.station).all()
    i =0
    all_stations = []
    for station in results:
        all_stations.append(station.station)
    return jsonify (all_stations)

@app.route("/api/v1.0/tobs")
def lastYearTemps():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last, = last_date
    #converts date string to datetime
    last_dt = dt.datetime.strptime(last, "%Y-%m-%d")
    #calc one year prior as date time object
    one_year_prior_dt = last_dt - (dt.timedelta(days= 365))
    #converts datetime object to string
    one_year_prior = one_year_prior_dt.strftime("%Y-%m-%d" )

    #queries for tobs between date contained within last  and one_year_prior 
    results =session.query(Measurement.tobs).filter(Measurement.date >= one_year_prior).all()
    all_tobs = list(np.ravel(results))
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def minAvgMaxTemps (start):
    """Return a JSON list of the minimum temperature, the average temperature,
     and the max temperature for a given starting date to the last date in the dataset."""
    
    #queries for max, min, and avg temperatures between the start date last recorded date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    #converts three results into a list
    results = list(np.ravel(results))
    
    results_list = []
    
    max_dict = {}
    max_dict["max_temp"] = results[0]
    results_list.append(max_dict)
    
    min_dict = {}
    min_dict["min_temp"] = results[1]
    results_list.append(min_dict)
    
    avg_dict= {}
    avg_dict["avg_temp"] = results[2]
    results_list.append(avg_dict)
    
    return jsonify(results_list)

@app.route("/api/v1.0/<start>/<end>")
def minAvgMaxTempsWithEnd (start, end):
    """Return a JSON list of the minimum temperature, the average temperature,
     and the max temperature for a given starting date to the end date (if the end date is prior to the last date recorded in the dataset)."""
    #queries for max, min, and avg temperatures between the start and end dates
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    #converts three results into a list
    results = list(np.ravel(results))
    
    results_list = []
    
    max_dict = {}
    max_dict["max_temp"] = results[0]
    results_list.append(max_dict)
   
    min_dict = {}
    min_dict["min_temp"] = results[1]
    results_list.append(min_dict)
    
    avg_dict= {}
    avg_dict["avg_temp"] = results[2]
    results_list.append(avg_dict)
    
    return jsonify(results_list)
if __name__ == "__main__":
    app.run(debug=True)