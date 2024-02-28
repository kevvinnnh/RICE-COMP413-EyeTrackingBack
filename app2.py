from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from pymongo import MongoClient


app = Flask(__name__)

# MongoDB connection URI
uri = "mongodb+srv://Project5-Sophia:<password>@project5.bpvocwv.mongodb.net/?retryWrites=true&w=majority&appName=Project5"

# Create a MongoClient object
client = MongoClient(uri)

# Initialize Flask-PyMongo
app.config["MONGO_URI"] = uri
mongo = PyMongo(app)

# Set up the database
db = client.get_database("your_database_name")


# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Example route for testing MongoDB connection
@app.route('/test-mongodb-connection')
def test_mongodb_connection():
    try:
        client.admin.command('ping')
        return jsonify({"message": "Successfully connected to MongoDB!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/survey', methods=['POST'])
def submit_data():
    try:
        db = mongo.db  # Access the MongoDB database

        # Extract data from the request (assuming JSON data is sent in the request body)
        data = request.json

        # Example: Insert data into a collection
        db.your_collection.insert_one(data)

        return jsonify({"message": "Data submitted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Custom port 5001