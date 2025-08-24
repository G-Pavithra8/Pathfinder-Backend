from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import re
from auth import auth_bp, bcrypt
from help import help_bp
from db import db
from dotenv import load_dotenv  # add this

# Collections
colleges_collection = db['colleges']
users_collection = db['users']
help_requests_collection = db['help_requests']
# Load env variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")
CORS(app, supports_credentials=True)
bcrypt.init_app(app)
@app.route("/")
def home():
    return "Backend is running successfully 🎉"


@app.route('/api/test-mongo', methods=['GET'])
def test_mongo():
    try:
        # Try to fetch one document from the collection
        doc = colleges_collection.find_one()
        if doc:
            return jsonify({"status": "success", "message": "MongoDB connected!", "sample": str(doc)})
        else:
            return jsonify({"status": "success", "message": "MongoDB connected, but collection is empty."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
def parse_fee(fee_str):
    try:
        if not isinstance(fee_str, str):
            return {"min": 0, "max": 0, "display": "N/A"}

        # Debugging print (optional):
        print(f"Raw Fee String: {repr(fee_str)}")

        # Remove currency symbols, commas, non-breaking spaces, regular spaces
        clean = fee_str.replace("₹", "").replace(",", "").replace("\u00A0", "").replace(" ", "")
        
        parts = clean.split("-")
        if len(parts) == 2:
            min_fee = int(parts[0])
            max_fee = int(parts[1])
            return {"min": min_fee, "max": max_fee, "display": fee_str}
        else:
            return {"min": 0, "max": 0, "display": "N/A"}
    except Exception as e:
        print(f"Fee parse error: {e}")
        return {"min": 0, "max": 0, "display": "N/A"}




@app.route('/api/colleges', methods=['GET'])
def get_colleges():
    try:
        name = request.args.get('name', '').lower().strip()
        fee_range = request.args.get('fee_range')
        course = request.args.get('course', '').lower().strip()
        max_cutoff = request.args.get('max_cutoff', type=float)

        colleges = list(colleges_collection.find())
        filtered = []

        if colleges:
            print("Document keys:", list(colleges[0].keys()))

        for college in colleges:
            try:
                college_name = college.get('College Name', '')
                fee_str = college.get('Fee Structure', '')  
                cutoff_raw = college.get('Cutoff', '')  
                rank = college.get('Rank', "N/A")

                # Fee & cutoff parsing
                fee = parse_fee(fee_str)
                try:
                    cutoff_val = float(cutoff_raw)
                except:
                    cutoff_val = None

                # Courses
                course_details = college.get('Course Details', '')
                courses = [c.strip() for c in course_details.split(',') if c.strip()]

                # Apply filters safely
                if name and name not in college_name.lower():
                    continue
                if course and course != "all courses" and not any(course in c.lower() for c in courses):
                    continue
                if max_cutoff and cutoff_val and cutoff_val > max_cutoff:
                    continue
                if fee_range and fee_range != "all":
                    if fee_range == "below_50k" and fee['min'] >= 50000:
                        continue
                    elif fee_range == "50k_to_80k" and (fee['min'] < 50000 or fee['max'] > 80000):
                        continue
                    elif fee_range == "above_80k" and fee['max'] <= 80000:
                        continue

                filtered.append({
                    'name': college_name,
                    'fee': fee['display'],
                    'courses': courses,
                    'cutoff': str(cutoff_raw) if cutoff_raw else "",
                    'rank': rank
                })

            except Exception as row_err:
                print(f"Error processing college: {row_err}")
                continue

        return jsonify(filtered)
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = set()
    for college in colleges_collection.find():
        course_details = college.get('Course Details', '')
        # Split by comma or semicolon, strip whitespace
        for course in re.split(r',|;', course_details):
            course = course.strip()
            if course:
                courses.add(course)
    return jsonify(sorted(list(courses)))


@app.route('/api/colleges', methods=['POST'])
def add_college():
    try:
        data = request.get_json()
        colleges_collection.insert_one(data)
        return jsonify({"status": "success", "message": "College added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


app.register_blueprint(auth_bp)
app.register_blueprint(help_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)