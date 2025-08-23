from flask import Blueprint, request, jsonify, session
from datetime import datetime
from pymongo import MongoClient
from db import db 

help_bp = Blueprint('help', __name__)

# You can import db from your main app if you set it up as a package,
# or re-create the connection here (safe for small apps)
client = MongoClient("mongodb://localhost:27017/")
db = client["pathfinder"]
help_requests = db["help_requests"]

@help_bp.route('/api/help', methods=['POST'])
def submit_help():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json
    message = data.get('message')
    email = data.get('email')

    if not message:
        return jsonify({'error': 'Message required'}), 400
    if not email:
        return jsonify({'error': 'Email required'}), 400

    help_requests.insert_one({
        'email': email,
        'message': message,
        'timestamp': datetime.utcnow()
    })
    return jsonify({'message': 'Help request submitted!'}), 201
