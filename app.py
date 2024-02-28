from flask import Flask, jsonify, request
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection URI
uri = "mongodb+srv://Project5-Sophia:<password>@project5.bpvocwv.mongodb.net/?retryWrites=true&w=majority&appName=Project5"

# Create a MongoClient object
client = MongoClient(uri)

# Set up the database
db = client.get_database("your_database_name")

@app.route('/')
def hello_world():
  return 'Hello, World!'

@app.route('/survey', methods=['POST'])
def save_survey_data():
    survey_data = request.json  # Assuming survey data is sent in JSON format
    db.surveys.insert_one(survey_data)
    return 'Survey data saved successfully', 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Custom port 5001