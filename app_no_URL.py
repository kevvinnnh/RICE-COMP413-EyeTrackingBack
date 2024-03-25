import json
from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from schemas import Participant, Response, UserForm, Creator, Form, Question
import random
import datetime
import string
import bcrypt
from gridfs import GridFS
from bson import json_util

app = Flask(__name__)
CORS(app)

# MongoDB connection URI
uri = "mongodb+srv://Project5-Sophia:koch@project5.bpvocwv.mongodb.net/?retryWrites=true&w=majority&appName=Project5"

# Create a MongoClient object
client = MongoClient(uri)



# Set up the database
db = client.get_database("EpiDerm")
fs = GridFS(db)


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
        participant_collection = db.get_collection("Participants")
        creator_collection = db.get_collection("Creators")
        if participant_collection.find_one({"email": email}) or creator_collection.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 400

        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Generate a unique user ID
        user_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        # Store user data in the respective collection based on role
        if role == "participant":
            participant_collection.insert_one({
                "email": email,
                "userId": user_id,
                "password": hashed_password
            })
        elif role == "creator":
            creator_collection.insert_one({
                "email": email,
                "userId": user_id,
                "password": hashed_password
            })

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

        # Add a dateCreated field with the current date and time
        dateCreated = datetime.datetime.now().isoformat()

        # Add the generated fields to the form data
        form_data['dateCreated'] = dateCreated

        collection = db.get_collection("Forms")
        inserted_id = collection.insert_one(form_data).inserted_id
        print(inserted_id)

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
        answers = ['Benign keratosis-like lesions','Melanocytic nevi','Benign keratosis-like lesions']
        count=0
        response_dict = {}
        print("collection 0")
        for i in range(len(answers)):
            index = str(i)
            response_dict[index] = responses_data[index]
            if responses_data[index] == answers[i]:
                count+=1
        print("collection 1")
        collection = db.get_collection("Responses")
        print("collection 2")
        inserted_ids = collection.insert_one({"user_id": 0,"form_id": 0, "role": responses_data["role"], "years_of_experience": responses_data["experienceLevel"],
                                            "age": responses_data["age"],"vision_impairment": responses_data["vision"], "gender": responses_data["gender"],"correctness_score": count,
                                            "eye_tracking_data": [], "responses": response_dict}).inserted_id
        print(inserted_ids)
        print("collection 2")
        return jsonify({"status": "success", "message": "Responses received and stored successfully"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# route for getting the responses and grading their form
@app.route('/api/get_responses', methods=['POST'])
def get_responses():
    try:
        # Get the responses data from the request JSON
        responses_data = request.json

        # Retrieve the questions for the form from the database
        form_id = responses_data.get('form_id')
        form_name = responses_data.get('form_name')
        form_questions = Question.objects(form_name = form_name)

        # Initialize correctness score and a dictionary to store responses
        correctness_score = 0
        user_responses = {}

        # Loop through each question in the form
        for question in form_questions:
            question_id = str(question.question_id)
            correct_answer = question.correct_answer

            # Check if the user's response matches the correct answer
            user_answer = responses_data.get(question_id)
            user_responses[question_id] = user_answer

            if user_answer == correct_answer:
                correctness_score += 1

        # Calculate the percentage correctness score
        total_questions = len(form_questions)
        percentage_score = (correctness_score / total_questions) * 100

        # Store the response in the database
        new_response = Response(
            user_id=responses_data.get('user_id'),
            form_id=form_id,
            role=responses_data.get('role'),
            years_of_experience=responses_data.get('years_of_experience'),
            age=responses_data.get('age'),
            gender=responses_data.get('gender'),
            vision_impairment=responses_data.get('vision_impairment'),
            correctness_score=percentage_score,
            responses=user_responses
        )
        new_response.save()

        return jsonify({"status": "success", "message": "Responses checked and stored successfully"}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#new route to get all forms' information and contents
@app.route('/api/forms', methods=['GET'])
@cross_origin()
def get_all_forms():
    try:
        forms = list(db.get_collection("Forms").find({}))
        data = json.loads(json_util.dumps(forms))
        return jsonify({"status": "success", "forms": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/forms', methods=['DELETE'])
@cross_origin()
def delete_all_forms():
    try:
        collection = db.get_collection("Forms")
        collection.delete_many({})
        return jsonify({"status": "success", "message": "All forms deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


#  this route is for creating the questions and adding images to the respective images
@app.route('/api/create_question', methods=['POST'])
def create_question():
    try:
        # Parse request data
        question_text = request.form['question_text']
        question_type = request.form['question_type']
        options = request.form.getlist('options')  # If applicable
        correct_answer = request.form['correct_answer']

        # Check if image is included in the request
        if 'image' in request.files:
            image_file = request.files['image']
            # Save the image to GridFS
            image_id = fs.put(image_file, filename=image_file.filename)
            # Construct the URL to retrieve the uploaded image
            image_url = f"/api/get_image/{image_id}"
        else:
            image_url = None

        # Save the question data to MongoDB
        question_data = {
            "question_text": question_text,
            "question_type": question_type,
            "options": options,
            "correct_answer": correct_answer,
            "image_url": image_url
        }
        # Save question data to your questions collection
        # Your code to save the question_data to MongoDB goes here

        return jsonify({"status": "success", "message": "Question created successfully", "question_data": question_data}), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
