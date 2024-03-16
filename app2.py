import json
from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
import random
import datetime
import string
import bcrypt


app = Flask(__name__)
CORS(app)

# MongoDB connection URI
uri = "mongodb+srv://Project5-Sophia:koch@project5.bpvocwv.mongodb.net/?retryWrites=true&w=majority&appName=Project5"

# Create a MongoClient object
client = MongoClient(uri)

# Set up the database
db = client.get_database("EpiDerm")

# this is for testing
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Define user roles (participant, creator, admin)
ROLES = ["participant", "creator", "admin"]

# Collection for storing user data

@app.route('/register', methods=['POST'])
@cross_origin()
def register_user():
    try:
        data = request.json
        email = data.get('email')
        role = data.get('role')

        # Validate email and role
        if not email or not role or role not in ROLES:
            return jsonify({"error": "Invalid email or role"}), 400

        # Check if the email is already registered
        if users_collection.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 400

        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Generate a unique user ID
        user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        # Store user data in the respective collection based on role
        if role == "participant":
            participants_collection.insert_one({
                "email": email,
                "userId": user_id,
                "password": hashed_password
            })
        elif role == "creator":
            creators_collection.insert_one({
                "email": email,
                "userId": user_id,
                "password": hashed_password
            })
        # Optionally can add handling for other roles ( admin?) here
        #need to make sure schema definition aligns 
        return jsonify({
            "message": "User registered successfully",
            "email": email,
            "role": role,
            "user_id": user_id,
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/forms', methods=['POST'])
@cross_origin()
def create_form():
    try:
        form_data = request.json
        # Generate a unique alphanumeric formID
        formID = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        # Add a dateCreated field with the current date and time
        dateCreated = datetime.datetime.now().isoformat()
        # Add the generated fields to the form data
        form_data['formID'] = formID
        form_data['dateCreated'] = dateCreated

        collection = db.get_collection("Forms")
        inserted_id = collection.insert_one(form_data).inserted_id

        return jsonify({"status": "success", "message": "Form added successfully", "insertedId": str(inserted_id)}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/questions', methods=['POST'])
@cross_origin()
def receive_questions():
    try:
        questions_data = request.json
        # Save the received questions to the database or perform any necessary processing
        collection = db.get_collection("Questions")
        inserted_ids = collection.insert_many(questions_data).inserted_ids

        return jsonify({"status": "success", "message": "Questions received and stored successfully", "insertedIds": inserted_ids}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/questions', methods=['GET'])
@cross_origin()
# this returns the questions to the frontend from the database
def get_questions():
    try:
        collection = db.get_collection("Questions")
        questions = list(collection.find())
        return jsonify({"status": "success", "questions": questions}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test', methods=['GET'])
def test_atlas_connection():
    try:
        collection = db.get_collection("Tests")
        result = collection.insert_one({"test": "connection"})
        return jsonify({"status": "success", "message": "Connected to MongoDB Atlas and inserted a document.", "insertedId": str(result.inserted_id)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/responses', methods=['POST'])
@cross_origin()
def receive_responses():
    try:
        responses_data = request.json
        print(responses_data)
        # Eventually, we can store the default survey in the database & it would act as a created survey
        answers = ['Benign keratosis-like lesions','Melanocytic nevi','Benign keratosis-like lesions']
        count=0
        # Function that grades hard coded default survey skin lesion questions
        for i in range(len(answers)):
            index = str(i)
            if responses_data[index] == answers[i]:
                count+=1

        # Save the received responses to the database or perform any necessary processing
        # collection = db.get_collection("Questions")
        # inserted_ids = collection.insert_many(responses_data).inserted_ids

        return jsonify({"status": "success", "message": "Responses received and stored successfully"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#new route to get all forms' information and contents
@app.route('/api/forms', methods=['GET'])
@cross_origin()
def get_all_forms():
    try:
        forms = list(db.Forms.find({}, {"_id": 0}))
        return jsonify({"status": "success", "forms": forms}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5001)
