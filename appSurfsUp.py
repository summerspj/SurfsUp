import numpy as np
import pandas as pd
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
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/'start date'              (Enter start date in format YYYY-MM-DD) <br/> "
        f"/api/v1.0/'start date'/'end date'   (Enter start and date date in format YYYY-MM-DD) <br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all dates/precipitation"""
    # Query all precipitation/dates
    try: 
        results = session.query(measurement.date, measurement.prcp).all()
        # serialized = [get_user_serialized(item) for item in x]
        print(results)

        all_precip = []

        for precip in results:
            precip_dict = {}
            precip_dict["date"] = precip[0]
            precip_dict["prcp"] = precip[1]
            all_precip.append(precip_dict)
        session.commit()
        return jsonify(all_precip)

    except Exception:
            print("Error")
            session.rollback()

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    try: 
        results = session.query(station.id, station.station, station.name).all()

        # Create a dictionary from the row data and append to a list of all_passengers
        all_stations = []

        for stat in results:
            station_dict = {}
            station_dict["id"] = stat[0]
            station_dict["station"] = stat[1]
            station_dict["name"] = stat[2]
            all_stations.append(station_dict)
        session.commit()
    except Exception:
        print("Error")
        session.rollback()

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of last 12 months of temperatures"""
    try: 
        current_time = dt.date.today()
        date = session.query(measurement.date, measurement.tobs).\
            order_by(measurement.date.desc()).first()

        year_ago = dt.datetime.strptime(date[0], "%Y-%m-%d") - dt.timedelta(days=366)

        sel=[measurement.date, measurement.tobs]
        # Query all stations
        results = session.query(*sel).filter(measurement.date >= year_ago).all()
        
        all_tobs = []
        for tobs_in in results:
            tobs_dict = {}
            tobs_dict["date"] = tobs_in[0]
            tobs_dict["tobs"] = tobs_in[1]
            all_tobs.append(tobs_dict)
        session.commit()
    except Exception:
        print("Error")
        session.rollback()

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start_date(start=None):
    # return min, average, max temps for all dates >= start date
    try: 
        sel=[measurement.date, measurement.tobs]
        results = session.query(*sel).filter(measurement.date >= start).all()
        
        sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)] 
        sta_averages = session.query(*sel).\
            filter(measurement.date >= start).all()
        summary = []
        for smry in sta_averages:
            smry_dict = {}
            smry_dict["min"] = smry[0]
            smry_dict["max"] = smry[1]
            smry_dict["avg"] = smry[2]
        summary.append(smry_dict)
        session.commit()
    except Exception:
        print("Error")
        session.rollback()
   
    return jsonify(summary)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # return min, average, max temps for all dates >= start date <= end date
    try: 
        sel=[measurement.date, measurement.tobs]
        results = session.query(*sel).filter(measurement.date >= start).\
            filter(measurement.date <= end).all()
        print(start)
        print(end)
        
        sel2 = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)] 
        sta_averages2 = session.query(*sel2).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end).all()
        summary2 = []
        for smry2 in sta_averages2:
            smry2_dict = {}
            smry2_dict["min"] = smry2[0]
            smry2_dict["max"] = smry2[1]
            smry2_dict["avg"] = smry2[2]
        summary2.append(smry2_dict)
        session.commit()
    except Exception:
        print("Error")
        session.rollback()

    return jsonify(summary2)

session.close()
if __name__ == '__main__':
    app.run(debug=True)
