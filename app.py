from pymongo import MongoClient
from datetime import datetime
from flask import Flask,request,render_template,jsonify
from flask_cors import CORS

client=MongoClient("mongodb+srv://meghanam0211:meghana0211@cluster0.donnu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client['contactless-lock']
collection=db['iotdata-test']
alertsCollection=db['alerts']
devicesCollection=db['devices']

api=Flask(__name__)
CORS(api)

@api.route('/')
def homePage():
    return jsonify({"message":"API Server Running"}), 200

@api.route('/alert', methods=['GET'])
def createAlert():
    """Store data in MongoDB using GET method."""
    type1 = request.args.get('type')
    message1 = request.args.get('message')

    if not type1 or not message1:
        return jsonify({"error": "Missing 'type' or 'message' query parameter."}), 400

    # Insert data with timestamp
    data = {
        "type": type1,
        "message": message1,
        "timestamp": datetime.utcnow()  # Add current UTC timestamp
    }
    result = alertsCollection.insert_one(data)
    data["_id"] = str(result.inserted_id)  # Convert ObjectId to string for JSON serialization

    return jsonify({"message": "Alert stored successfully", "data": data}), 201

@api.route('/store', methods=['GET'])
def store_data():
    """Store data in MongoDB using GET method."""
    label = request.args.get('label')
    value = request.args.get('value')

    if not label or not value:
        return jsonify({"error": "Missing 'label' or 'value' query parameter."}), 400

    try:
        value = float(value)  # Convert value to numeric
    except ValueError:
        return jsonify({"error": "'value' must be a numeric type."}), 400

    # Insert data with timestamp
    data = {
        "label": label,
        "value": value,
        "timestamp": datetime.utcnow()  # Add current UTC timestamp
    }
    result = collection.insert_one(data)
    data["_id"] = str(result.inserted_id)  # Convert ObjectId to string for JSON serialization

    return jsonify({"message": "Data stored successfully", "data": data}), 201

@api.route('/get-data', methods=['GET'])
def get_data():
    """Retrieve data from MongoDB."""
    # Retrieve data and convert ObjectId to string if necessary
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data)

@api.route('/get-alerts', methods=['GET'])
def get_alerts():
    """Retrieve data from MongoDB."""
    # Retrieve data and convert ObjectId to string if necessary
    data = list(alertsCollection.find({}, {"_id": 0}))
    return jsonify(data)

@api.route('/toggle-device', methods=['POST'])
def toggle_device():
    """Toggle the state of a device."""
    try:
        # Get device_id from the request body
        data = request.json
        device_id = data.get("device_id")

        if not device_id:
            return jsonify({"error": "Missing 'device_id' parameter."}), 400

        # Find the device in the database
        device = devicesCollection.find_one({"device_id": device_id})
        if not device:
            return jsonify({"error": f"Device with ID {device_id} not found."}), 404

        # Toggle the state of the device
        new_state = "on" if device.get("state", "off") == "off" else "off"
        devicesCollection.update_one({"device_id": device_id}, {"$set": {"state": new_state}})

        return jsonify({"message": f"Device {device_id} toggled", "state": new_state}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/get-devices', methods=['GET'])
def get_devices():
    """Retrieve all devices and their states."""
    try:
        devices = list(devicesCollection.find({}, {"_id": 0}))  # Exclude MongoDB ObjectId
        return jsonify(devices), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=2000,debug=True)
