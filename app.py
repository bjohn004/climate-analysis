#import dependencies
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

# flask dependncies
from flask import Flask, jsonify
#------------------------------------------------

# create engine
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# -----------------------------------------------
# Flask Setup
app = Flask(__name__)

# Flask Routes
# -----------------------------------------------
# Home Page
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Find all your Climate info Here!<br/>"
        f" <br/>"
        f"Available Routes:<br/>"
        f" <br/>"
        f"/api/v1.0/precipitation<br/>"
        f" <br/>"
        f"/api/v1.0/tobs<br/>"
        f" <br/>"
        f"/api/v1.0/start_date/year-month-date<br/>"
        f" <br/>"
        f"/api/v1.0/start_date/year-month-date/end_date/year-month-date<br/>"
        f" <br/>"
        f"Note that year-month-date is in the format of 2015-04-01"
    )

# -----------------------------------------------
# Precipitation Page
@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    all_precips = dict(results)  

    return jsonify(all_precips)

# -----------------------------------------------
# Stations Page
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# -----------------------------------------------
# TOBS Page
@app.route("/api/v1.0/tobs")
def temp():

    session = Session(engine)
    date_end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    date_end = dt.date(2017, 8, 23)
    date_begin = date_end - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= date_begin).\
                filter(Measurement.date <= date_end).all()
    
    session.close()
    
    all_temps =[]
    for date, temperature in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = temperature
        all_temps.append(temp_dict)
    

    return jsonify(all_temps)

# -----------------------------------------------
# # Start Date Page
# @app.route("/api/v1.0/start_date/<start_date>")
# def start(start_date):

# Start Date Page
@app.route("/api/v1.0/start_date/<start_date>")
def start(start_date):

# ------------ change start date to integers from URL entry into datetime to help with query ------------
    session = Session(engine)

    start_date = start_date.split("-")

    start_date = dt.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))

    all_dates = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()
    
    dates_list = []
 
    for min, max, avg in all_dates:
        date_temp = {}
        date_temp["Minimum"] = min
        date_temp["Maximum"] = max
        date_temp["Average"] = round(avg,2)
        dates_list.append(date_temp)
    return jsonify(start_date, dates_list[0])
   
# -----------------------------------------------
# Start and End Date Page
@app.route("/api/v1.0/start_date/<start_date>/end_date/<end_date>")
def start_end(start_date, end_date):

# ------------ change start date to integers from URL entry into datetime to help with query ------------
    session = Session(engine)

    start_date = start_date.split("-")
    end_date =  end_date.split("-")
    start_date = dt.date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
    end_date = dt.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
    all_dates = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()

    session.close()
    
    dates_list = []
 
    for min, max, avg in all_dates:
        date_temp = {}
        date_temp["Minimum"] = min
        date_temp["Maximum"] = max
        date_temp["Average"] = round(avg,2)
        dates_list.append(date_temp)
    
    # return the start and end date along with the min/max/avg
    return jsonify(start_date, end_date, dates_list[0])
    


if __name__ == '__main__':
    app.run(debug = True)