# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd


from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)
#################################################


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

print(Base.classes.keys())

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
app = Flask(__name__)
#################################################


#################################################
# 1. Flask Routes
@app.route("/")
def homepage():

    return (
        f"Welcome, Here all the available route to Hawaii temp:<br/>"
        f"/api/v1.0/precipitation<br/r>"
        f"/api/v1.0/stations<br/r>"
        f"/api/v1.0/tobs<br/r>"
        f"/api/v1.0/<start><br/r>"
        f"/api/v1.0/<end><br/r>"
    )

# 2. Precipitation Routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create our session (link) from Pythone to the DB
    session = Session(engine)

    # The Most recent Date
    most_recent_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()[0]
    
    one_year_ago = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    
    

    #Query all precipitation
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago.strftime('%Y-%m-%d')).\
    order_by(Measurement.date).all()

    session.close()
    
    #create an empty list and added each values in to a dictionary
    results = []
    for date, date_prcp in precipitation_data:
        results.append({date : date_prcp})

    return jsonify (results)
    
# 3. Station Routes 
@app.route("/api/v1.0/stations")
def station():

    #create our session (link) from Pythone to the DB
    session = Session(engine)

    #Query all station
    results = session.query(Station.station).all()

    session.close()

    #convert list of tuples into normal list
    all_names = list(np.ravel(results))
 
    return jsonify(all_names)

# 4. Temprature observed Routes
@app.route("/api/v1.0/tobs")
def temp():
    
    #Create our session (link) from Python to the DB
    session = Session(engine)

    # List the stations and their counts in descending order.
    active_station = session.query(Measurement.station, Measurement.date,
                                func.count(Measurement.id).label('measurement_count')) \
                         .group_by(Measurement.station) \
                         .order_by(func.count(Measurement.id).desc()) \
                         .first()
    
    one_year_ago = pd.to_datetime(active_station[1]) - pd.DateOffset(years=1)
   
    #create a list of temp for the
    query_of_temp = session.query(Measurement.tobs).filter(Measurement.station == active_station[0])\
                .filter(Measurement.date >= one_year_ago.strftime('%Y-%m-%d')).\
                order_by(Measurement.tobs).all()
    

    session.close()

    temp_list = list(np.ravel(query_of_temp))

    return jsonify(temp_list)

# 5. Start date Route
@app.route("/api/v1.0/<start>")
def start(start):


    start_date_obj = pd.to_datetime(start, format='%Y-%m-%d')
   
    #Create our session (link) from Python to the DB
    session = Session(engine)

    list_of_measurements = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    #Query all temp min, avg, and max
    temp = session.query(*list_of_measurements)\
                .filter(Measurement.date >= start_date_obj.strftime('%Y-%m-%d'))\
                .order_by(Measurement.tobs).all()
    
   
    # Unpack the results and prepare the JSON response
    temp_min, temp_avg, temp_max = temp[0]
    temp_data = {
        "TMIN": temp_min,
        "TAVG": temp_avg,
        "TMAX": temp_max
    }

    return jsonify(temp_data)


#6 Start end date route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    start_date_obj = pd.to_datetime(start, format='%Y-%m-%d')

    end_date_obj = pd.to_datetime(end, format='%Y-%m-%d')

    #Create our session (link) from Python to the DB
    session = Session(engine)

    list_of_measurements = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    #Query all temp min, avg, and max
    temp = session.query(*list_of_measurements)\
                .filter(Measurement.date >= start_date_obj.strftime('%Y-%m-%d'))\
                .filter(Measurement.date <= end_date_obj.strftime('%Y-%m-%d'))\
                .order_by(Measurement.tobs).all()
    
   
    # Unpack the results and prepare the JSON response
    temp_min, temp_avg, temp_max = temp[0]
    temp_data = {
        "TMIN": temp_min,
        "TAVG": temp_avg,
        "TMAX": temp_max
    }

    return jsonify(temp_data)




if __name__ == "__main__":
    app.run(debug=True)