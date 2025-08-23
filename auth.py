from flask import Blueprint, request, jsonify, session
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from db import db  

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

client = MongoClient("mongodb://localhost:27017/")
db = client["pathfinder"]
users_collection = db["users"]

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'error': 'All fields required'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    users_collection.insert_one({'email': email, 'password': hashed_pw, 'name': name})
    return jsonify({'message': 'Signup successful'}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user'] = str(user['_id'])
    return jsonify({'message': 'Login successful', 'name': user['name']}), 200

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'}), 200

@auth_bp.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user' in session:
        return jsonify({'authenticated': True})
    else:
        return jsonify({'authenticated': False})
