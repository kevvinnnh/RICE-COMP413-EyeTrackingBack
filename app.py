import requests
import json
from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection URI
uri = "mongodb+srv://Project5-Sophia:koch@project5.bpvocwv.mongodb.net/?retryWrites=true&w=majority&appName=Project5"

# Create a MongoClient object
client = MongoClient(uri)

# Set up the database
db = client.get_database("EpiDerm")

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/survey', methods=['POST'])
def save_survey_data():
  survey_data = request.json  # Assuming survey data is sent in JSON format
  db.surveys.insert_one(survey_data)
  return 'Survey data saved successfully', 201


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