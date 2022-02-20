from flask import Flask, request
from flask_cors import CORS

import requests
from util.consts import *

app = Flask(__name__)
CORS(app)

nrel_api_key = "slTk0Zgzbd1wRRMtssUP8fBWjLHNWHxIhurqB70P"


dcFastChargers = [
    {
        "name": "",
        "location": "",
    }
]

superChargers = [
    {
        "name": "",
        "location": "",
    }
]

location = [
    {
        "Starting_point": "",
    }
]


def getTimeAtCharger(battery_capacity, charging_speed, distance, car_speed):
    time_to_station = distance/car_speed  # hour

    charging_time = battery_capacity/charging_speed
    print(f"Charging Time: {charging_time} hours")

    net_time = round(charging_time + time_to_station, 5)
    print(f"Net Time: {net_time} hours")

    return net_time

def getTimeAtChargerWithMatrixAPI(battery_capacity, charging_speed, time_to_station):
    charging_time = battery_capacity/charging_speed
    print(f"Charging Time: {charging_time} hours")

    net_time = round(charging_time + time_to_station, 5)
    print(f"Net Time: {net_time} hours")

    return net_time

def distanceToCharger(curr_location, charger_location):
    pass
    # print(res.json)
  


@app.route('/', methods=['GET'])
def index():
    return 'hello'


@app.route('/api/findBestDCFastCharger', methods=['POST'])
def findClosestDCFastCharger():
    print(request.json)
    battery_capacity = request.json["batteryToFill"]  # Amount needed to fill, kWh
    curr_location = request.json["currLocation"] # Address or (lat, long)

    if isinstance(curr_location, list):
        req_str = f"https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={nrel_api_key}&country=all&latitude={curr_location[0]}&longitude={curr_location[1]}&limit=1&ev_charging_level=dc_fast"
    else:
        location = '+'.join(''.join([char for char in curr_location if char.isalnum() or char == " "]).split())
        print(location)
        req_str = f"https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={nrel_api_key}&country=all&location={location}&limit=1&ev_charging_level=dc_fast"

    fuelStationData = {}
    with requests.get(req_str) as res:
        resData = res.json()
        if resData["total_results"] > 0:
            fuelStationDataRaw = resData["fuel_stations"][0]
            fuelStationData = {
                "name": fuelStationDataRaw["station_name"],
                "phone_number": fuelStationDataRaw["station_phone"],
                "location": {
                    "coordinates": (fuelStationDataRaw["latitude"], fuelStationDataRaw["longitude"]),
                    "address": fuelStationDataRaw["street_address"],
                    "city": fuelStationDataRaw["city"],
                    "state": fuelStationDataRaw["state"],
                    "zip": fuelStationDataRaw["zip"],
                },
                "connector_types": fuelStationDataRaw["ev_connector_types"],
                "ev_network": fuelStationDataRaw["ev_network"],
                "distance": fuelStationDataRaw["distance_km"],
                "pricing": fuelStationDataRaw["ev_pricing"]
            }

    if isinstance(curr_location, list):
        req_str = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={curr_location[0]} {curr_location[1]}&destinations={fuelStationData['location']['address']}&key=AIzaSyA-2hrkZS4W_t37X-iYVB4XmeDwwmZC1Dk"
    else:
        req_str = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={curr_location}&destinations={fuelStationData['location']['address']}&key=AIzaSyA-2hrkZS4W_t37X-iYVB4XmeDwwmZC1Dk"
    
    response = requests.request("GET", req_str)
    minsToStation = response.json()["rows"][0]["elements"][0]["duration"]["value"] / 60

    net_time = getTimeAtChargerWithMatrixAPI(battery_capacity, DC_FAST_CHARGER_SPEED, minsToStation / 60)

    return {
        "net_time": net_time,
        "fuel_station": fuelStationData
    }

@app.route('/api/findBestLevel2Charger', methods=['POST'])
def findClosestLevel2Charger():
    print(request.json)
    battery_capacity = request.json["batteryToFill"]  # Amount needed to fill, kWh
    curr_location = request.json["currLocation"] # Address

    if isinstance(curr_location, list):
        req_str = f"https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={nrel_api_key}&country=all&latitude={curr_location[0]}&longitude={curr_location[1]}&limit=1&ev_charging_level=2"
    else:
        location = '+'.join(''.join([char for char in curr_location if char.isalnum() or char == " "]).split())
        print(location)
        req_str = f"https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={nrel_api_key}&country=all&location={location}&limit=1&ev_charging_level=2"
    
    fuelStationData = {}
    with requests.get(req_str) as res:
        resData = res.json()
        if resData["total_results"] > 0:
            fuelStationDataRaw = resData["fuel_stations"][0]
            fuelStationData = {
                "name": fuelStationDataRaw["station_name"],
                "phone_number": fuelStationDataRaw["station_phone"],
                "location": {
                    "coordinates": (fuelStationDataRaw["latitude"], fuelStationDataRaw["longitude"]),
                    "address": fuelStationDataRaw["street_address"],
                    "city": fuelStationDataRaw["city"],
                    "state": fuelStationDataRaw["state"],
                    "zip": fuelStationDataRaw["zip"],
                },
                "connector_types": fuelStationDataRaw["ev_connector_types"],
                "ev_network": fuelStationDataRaw["ev_network"],
                "distance": fuelStationDataRaw["distance_km"],
                "pricing": fuelStationDataRaw["ev_pricing"]
            }

    if isinstance(curr_location, list):
        req_str = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={curr_location[0]} {curr_location[1]}&destinations={fuelStationData['location']['address']}&key=AIzaSyA-2hrkZS4W_t37X-iYVB4XmeDwwmZC1Dk"
    else:
        req_str = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={curr_location}&destinations={fuelStationData['location']['address']}&key=AIzaSyA-2hrkZS4W_t37X-iYVB4XmeDwwmZC1Dk"
    
    response = requests.request("GET", req_str)
    minsToStation = response.json()["rows"][0]["elements"][0]["duration"]["value"] / 60

    net_time = getTimeAtChargerWithMatrixAPI(battery_capacity, LEVEL_2_CHARGER_SPEED, minsToStation / 60)

    return {
        "net_time": net_time,
        "fuel_station": fuelStationData
    }
    
@app.route('/api/findBestSupercharger', methods=['POST'])
def findClosestSupercharger():
    print(request.json)
    battery_capacity = request.json["batteryToFill"]  # Amount needed to fill, kWh
    curr_location = request.json["currLocation"] # Address

    if isinstance(curr_location, list):
        req_str = f"https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={nrel_api_key}&country=all&latitude={curr_location[0]}&longitude={curr_location[1]}&limit=1&ev_network=Tesla"
    else:
        location = '+'.join(''.join([char for char in curr_location if char.isalnum() or char == " "]).split())
        print(location)
        req_str = f"https://developer.nrel.gov/api/alt-fuel-stations/v1/nearest.json?api_key={nrel_api_key}&country=all&location={location}&limit=1&ev_network=Tesla"

    fuelStationData = {}
    with requests.get(req_str) as res:
        resData = res.json()
        if resData["total_results"] > 0:
            fuelStationDataRaw = resData["fuel_stations"][0]
            fuelStationData = {
                "name": fuelStationDataRaw["station_name"],
                "phone_number": fuelStationDataRaw["station_phone"],
                "location": {
                    "coordinates": (fuelStationDataRaw["latitude"], fuelStationDataRaw["longitude"]),
                    "address": fuelStationDataRaw["street_address"],
                    "city": fuelStationDataRaw["city"],
                    "state": fuelStationDataRaw["state"],
                    "zip": fuelStationDataRaw["zip"],
                },
                "connector_types": fuelStationDataRaw["ev_connector_types"],
                "ev_network": fuelStationDataRaw["ev_network"],
                "distance": fuelStationDataRaw["distance_km"],
                "pricing": fuelStationDataRaw["ev_pricing"]
            }

    if isinstance(curr_location, list):
        req_str = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={curr_location[0]} {curr_location[1]}&destinations={fuelStationData['location']['address']}&key=AIzaSyA-2hrkZS4W_t37X-iYVB4XmeDwwmZC1Dk"
    else:
        req_str = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={curr_location}&destinations={fuelStationData['location']['address']}&key=AIzaSyA-2hrkZS4W_t37X-iYVB4XmeDwwmZC1Dk"
    
    response = requests.request("GET", req_str)
    minsToStation = response.json()["rows"][0]["elements"][0]["duration"]["value"] / 60

    net_time = getTimeAtChargerWithMatrixAPI(battery_capacity, SUPERCHARGER_SPEED, minsToStation / 60)

    return {
        "net_time": net_time,
        "fuel_station": fuelStationData
    }

@app.route('/api/distanceToCharger', methods=['POST'])
def distanceToChargerEndpoint():
    # distanceToCharger(curr_location)
    return ''

if __name__ == '__main__':
    app.run(debug=True)