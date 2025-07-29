from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import re
from auth import auth_bp, bcrypt
from help import help_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong, random key!
CORS(app, supports_credentials=True)
bcrypt.init_app(app)

# Connect to MongoDB (local)
client = MongoClient("mongodb://localhost:27017/")
db = client["pathfinder"]  # Use your database name
colleges_collection = db["colleges"]  # Use your collection name

def parse_fee(fee_str):
    """Convert fee string to numeric range"""
    fee_str_clean = fee_str.replace('₹', '').replace(',', '').replace(' ', '')
    numbers = [int(num) for num in re.findall(r'\d+', fee_str_clean)]
    if len(numbers) == 1:
        return {'min': numbers[0], 'max': numbers[0], 'display': fee_str}
    elif len(numbers) >= 2:
        return {'min': min(numbers), 'max': max(numbers), 'display': fee_str}
    else:
        return {'min': 0, 'max': 0, 'display': "N/A"}

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

@app.route('/api/colleges', methods=['GET'])
def get_colleges():
    try:
        name = request.args.get('name', '').lower()
        fee_range = request.args.get('fee_range')
        course = request.args.get('course', '').lower()
        max_cutoff = request.args.get('max_cutoff', type=float)

        colleges = list(colleges_collection.find())
        filtered = []

        # Debug: print the keys of the first document
        if colleges:
            print(list(colleges[0].keys()))

        for college in colleges:
            try:
                college_name = college.get('College Name', '')

                # Use the correct field names with trailing spaces!
                fee_str = college.get('Fee Structure ', '')  # <-- Note the space!
                cutoff_raw = college.get('Cutoff ', '')      # <-- Note the space!
                rank = college.get('Rank', "N/A")

                # Parse Fee
                fee = parse_fee(fee_str) if fee_str else {'min': 0, 'max': 0, 'display': "N/A"}

                # Parse Cutoff
                try:
                    cutoff_val = float(cutoff_raw)
                except:
                    cutoff_val = None

                # Course list
                course_details = college.get('Course Details', '')
                courses = [c.strip() for c in course_details.split(',') if c.strip()]

                # Apply Filters
                if name and name not in college_name.lower():
                    continue
                if course and not any(course in c.lower() for c in courses):
                    continue
                if max_cutoff and cutoff_val and cutoff_val > max_cutoff:
                    continue
                if fee_range:
                    if fee_range == "below_50k" and fee['min'] >= 50000:
                        continue
                    elif fee_range == "50k_to_80k" and (fee['min'] < 50000 or fee['max'] > 80000):
                        continue
                    elif fee_range == "above_80k" and fee['max'] <= 80000:
                        continue
            
                # Append final college data
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

app.register_blueprint(auth_bp)
app.register_blueprint(help_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)