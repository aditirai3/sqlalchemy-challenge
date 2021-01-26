import numpy as np

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii<br/>"
        f"The available api routes are:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end_date>"
    )


@app.route("/api/v1.0/precipitation")
def prec():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Hawaii Precipitation"""
    # Run Query
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert to dictionary and return a list of dictionaries
    p_score =[]
    for date, pr in results:
        prep_dict = {}
        prep_dict["date"] = date
        prep_dict["prcp"] = pr
        p_score.append(prep_dict)

    return jsonify(p_score)

@app.route("/api/v1.0/stations")
def stat():
    # Return a JSON list of stations from the dataset
    session = Session(engine)
    """List of stations"""
    s_results = session.query(Station.station, Station.name).all()
    session.close()

    return jsonify(s_results)

@app.route("/api/v1.0/tobs")
def tob():
    session = Session(engine)
    #  Query the dates and temperature observations of the most active station for the last year of data 
    active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active = active_station[0][0]
    tob_result = session.query(Station.name, Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date=='2017-08-23').filter(Measurement.station==most_active)
    #  Return a JSON list of temperature observations (TOBS) for the previous year
    #  Calculate the last date and date of one year back
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    prev_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    #  Run query
    rest = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prev_year).all()
    session.close()
    # Display results in json
    final_result = []
    for d, t in rest:
        tob_dict={}
        tob_dict["date"] = d
        tob_dict["tobs"] = t
        final_result.append(tob_dict)
    return jsonify(final_result)

@app.route("/api/v1.0/<start_date>")
def s_date(start_date):
    session = Session(engine)
    s_date_result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date>=start_date).all()
    session.close()
    # Convert list of tuples into normal list
    start_result = list(np.ravel(s_date_result))
    return jsonify(start_result)

@app.route("/api/v1.0/<start_date>/<end_date>")
def date(start_date, end_date):
    session = Session(engine)
    date_result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
    session.close()
    abc = list(np.ravel(date_result))
    return jsonify(f"Minimum Temp is: {abc[0]} , Maximum Temp is: {abc[1]} and Average Temp is: {abc[2]}")

if __name__ == '__main__':
    app.run(debug=True)
