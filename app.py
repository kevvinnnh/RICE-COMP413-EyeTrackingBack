from flask import Flask, jsonify, request
from pymongo import MongoClient
app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']

@app.route('/users', methods=['GET'])
def get_users():
    users = list(db.users.find())
    return jsonify(users), 200

@app.route('/users', methods=['POST'])
def add_user():
    user_data = request.json
    db.users.insert_one(user_data)
    return 'User added successfully', 201

