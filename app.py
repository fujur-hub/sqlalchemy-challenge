import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
#-----------------------------#

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#In 6
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

##Flask Start
app = Flask(__name__)

##Routes

@app.route("/")
def welcome():
    return (
        f"Welcome to Angel's Hawaii trip Climate Observations API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/hightemp<br/>"
        f"/api/v1.0/trip"
    )

@app.route("/api/v1.0/precipitation")
def last_year_prcp():
    "Rainfall from last year"
    last_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    last_year_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > last_year).all()
    session.close()

    rainfall = {date: prcp for date, prcp in last_year_prcp}
    return jsonify(rainfall)

@app.route("/api/v1.0/stations")
def stations():
    "Stations in Hawaii"
    active_stations = session.query(Station.station).all()
    
    session.close()
    ##Titanic example
    stations = list(np.ravel(active_stations))
    return jsonify(stations)

@app.route("/api/v1.0/hightemp")
def high_temp():
    "Station with the highest Temperatures over the last year"
    last_year = dt.date(2017,8,23)-dt.timedelta(days=365)
    hist = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date > last_year).all()
    
    session.close()

    high_temp = list(np.ravel(hist))
    return jsonify(high_temp)

@app.route("/api/v1.0/trip")
def trip():
    "Angel's trip temps"

    start_date_ly = '2015-11-01'
    end_date_ly = '2015-11-10'

    trip_dates = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation,func.sum(Measurement.prcp)).\
        filter(Measurement.station == Station.station).\
        filter(Measurement.date >= start_date_ly).\
        filter(Measurement.date <=end_date_ly).\
        group_by(Station.name).\
        order_by(func.sum(Measurement.prcp).desc()).all()[0]

    session.close()

    trip = list(np.ravel(trip_dates))
    return jsonify(trip)
    
    
if __name__ == '__main__':
    app.run()