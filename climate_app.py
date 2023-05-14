#Part 2: Design Climate App
# dependencies.

from flask import Flask, jsonify
import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///SurfsUp/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#Flask API Base
app = Flask(__name__)

#1 Home Page and list of available routes

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"<h3>Available Routes:</h3><br/>"
        f"<b>Precipitation observations for the last 12 months of data:</b><br/><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<br/><b>Weather stations:</b><br/><a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<br/><b>Temperature observations for the last 12 months of the data:</b> <br/><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<br/><b>Temperature summary for a specific date:</b><br/>(replace place holders with date)<br/><a href='/api/v1.0/2016-08-23'>/api/v1.0/2016-08-23</a><br/>"
        f"<br/><b>Temperature summary for a date range:</b><br/>(replace place holders with dates)<br/><a href='/api/v1.0/2016-08-23/2017-08-23'>/api/v1.0/2016-08-23/2017-08-23</a><br/>"
    )
##################################################################################################
#2 Convert the query results from your precipitation analysis. 
#  Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
  Session = sessionmaker(bind=engine)
  session = Session()
  order_by_dates = session.query(measurement.date).order_by(measurement.date.desc())
  recent_date = dt.date.fromisoformat(order_by_dates[0][0])
  twelve_months_ago = recent_date - dt.timedelta(days=365)
  
  prcp_scores = session.query(measurement.date, measurement.prcp).filter(measurement.date >= twelve_months_ago).\
    order_by(measurement.date).all()
  session.close()

  prcp_dict = {}
  for date, prcp in prcp_scores:
    prcp_dict[date] = prcp

  return jsonify(prcp_dict)
########################################################################################

#3 Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station_list():
  Session = sessionmaker(bind=engine)
  session = Session()
  active_stations_total = session.query(measurement.station, func.count(measurement.station)).\
                    group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
  session.close()

  #active_stations_total
  station_id = []
  for station, _ in active_stations_total:
    station_id.append(station)
  return jsonify(station_id)
#######################################################################################

#4 Query the dates and temperature observations of the most-active station for the previous year of data. 
# Return a JSON list of temperature observations for the previous year. 
@app.route("/api/v1.0/tobs")
def temps():

    session = Session(engine)
    active_stations_total = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station = active_stations_total[0][0]

    order_by_dates = session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        order_by(measurement.date.desc())
    recent_date = dt.date.fromisoformat(order_by_dates[0][1])
    twelve_months_ago = recent_date - dt.timedelta(days=365)
    observation_data = order_by_dates.filter(measurement.date >= twelve_months_ago).all()
    session.close()

    temperatures = []
    for station,date,tobs in observation_data:
      temperatures.append([station, date, tobs])
    return jsonify(temperatures)


##################################################################################

#5 Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>", defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def temp_details(start, end):

    session = Session(engine)
    start_date = dt.date.fromisoformat(start)
    query = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))
    query = query.filter(measurement.date >= start_date)
    if end is not None:
      end_date = dt.date.fromisoformat(end)
      query = query.filter(measurement.date <= end_date)
    query = query.group_by(measurement.date)

    temp_stats = query.all()
    session.close()


    temp_score = []
    for date, min, avg, max in temp_stats:
      temp_score.append([date, min, avg, max])
    return jsonify(temp_score)




if __name__ == '__main__':
    app.run(debug=True)