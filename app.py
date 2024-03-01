import requests
import json
from flask import Flask, jsonify, request
from pymongo import MongoClient

from flask_cors import CORS, cross_origin

import random
import datetime
import string

app = Flask(__name__)
CORS(app)

# MongoDB connection URI
uri = "mongodb+srv://Project5-Sophia:koch@project5.bpvocwv.mongodb.net/?retryWrites=true&w=majority&appName=Project5"

# Create a MongoClient object
client = MongoClient(uri)

# Set up the database
db = client.get_database("EpiDerm")

@app.route('/')
def hello_world():
  return 'Hello, World!'


@app.route('/api/forms', methods=['POST'])
@cross_origin()  # This enables CORS specifically for this route
def create_form():
    print("create_form:", request.json)

    form_data = request.json  # Assuming form data is sent in JSON format
    # Generate a unique alphanumeric formID
    formID = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    # Add a dateCreated field with the current date and time
    dateCreated = datetime.datetime.now().isoformat()
    # Add the generated fields to the form data
    form_data['formID'] = formID
    form_data['dateCreated'] = dateCreated

    url = "https://us-east-2.aws.data.mongodb-api.com/app/data-bpzpl/endpoint/data/v1/action/insertOne"
    payload = json.dumps({
        "collection": "Forms",
        "database": "EpiDerm",
        "dataSource": "Project5",
        "document": form_data
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': 'yJAaJITqsyGpxeQ3gEZIsip2M6o0iWp6jpdddoGJY4WZ2PgPVEaGRqgRjY2SjZJ2',
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()
        if response.status_code == 200 and response_data.get('insertedId'):
            return jsonify({"status": "success", "message": "Form added successfully", "insertedId": response_data['insertedId']}), 201
        else:
            return jsonify({"status": "error", "message": "Failed to add form"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Succesfully adds a document to the "Tests" collection
@app.route('/test', methods=['GET'])
def test_atlas_connection():
    url = "https://us-east-2.aws.data.mongodb-api.com/app/data-bpzpl/endpoint/data/v1/action/insertOne"
    payload = json.dumps({
        "collection": "Tests",
        "database": "EpiDerm",
        "dataSource": "Project5",
        "document": {
            "test": "connection"
        }
    })
    headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key': 'yJAaJITqsyGpxeQ3gEZIsip2M6o0iWp6jpdddoGJY4WZ2PgPVEaGRqgRjY2SjZJ2',
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        return jsonify({"status": "success", "message": "Connected to MongoDB Atlas and inserted a document.", "response": response.json()}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Custom port 5001