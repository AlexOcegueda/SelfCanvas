from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Import BOTH parsers now
from importers import parse_mit_assignments, parse_mit_json

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canvas.db'
db = SQLAlchemy(app)

# --- MODELS ---
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    modules = db.relationship('Module', backref='course', lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)

# --- ROUTES ---

# Add this inside backend/app.py

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    
    # 1. Validate Input
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
        
    title = data['title'].strip()
    if not title:
         return jsonify({"error": "Title cannot be empty"}), 400

    try:
        # 2. Check for duplicate names (Optional but recommended)
        existing = Course.query.filter_by(title=title).first()
        if existing:
             return jsonify({"error": "Course already exists"}), 400

        # 3. Create & Save
        new_course = Course(title=title)
        db.session.add(new_course)
        db.session.commit()
        
        return jsonify({
            "message": "Course created successfully",
            "course": {"id": new_course.id, "title": new_course.title}
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    output = []
    for course in courses:
        output.append({'id': course.id, 'title': course.title})
    return jsonify(output)

@app.route('/api/course/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    course = Course.query.get_or_404(course_id)
    
    modules_list = []
    for module in course.modules:
        modules_list.append({
            "id": module.id,
            "title": module.title,
            "content": module.content
        })

    return jsonify({
        "id": course.id,
        "title": course.title,
        "modules": modules_list
    })

@app.route('/api/upload-mit-assignments', methods=['POST'])
def upload_mit_assignments():
    course_id = request.form.get('course_id')
    file = request.files.get('file')

    if not file or not course_id:
        return jsonify({"error": "Missing file or course_id"}), 400

    filename = file.filename.lower()
    content = file.read().decode('utf-8', errors='ignore')
    
    extracted_data = []

    # --- WATERFALL LOGIC ---
    # 1. Try JSON
    if filename.endswith('.json'):
        print(f"Processing JSON file for Course {course_id}")
        extracted_data = parse_mit_json(content)
        
    # 2. Try HTML
    elif filename.endswith('.html') or filename.endswith('.htm'):
        print(f"Processing HTML file for Course {course_id}")
        extracted_data = parse_mit_assignments(content)
        
    else:
        return jsonify({"error": "Unsupported file type. Please upload .html or .json"}), 400

    # Check for parser errors
    if isinstance(extracted_data, dict) and "error" in extracted_data:
        return jsonify(extracted_data), 400
    
    if not extracted_data:
        return jsonify({"message": "File parsed but no assignments were found."}), 200

    # 3. Save to Database
    try:
        saved_count = 0
        for item in extracted_data:
            exists = Module.query.filter_by(course_id=course_id, title=item['title']).first()
            if not exists:
                new_module = Module(
                    course_id=course_id, 
                    title=item['title'],
                    content=item['content']
                )
                db.session.add(new_module)
                saved_count += 1
        
        db.session.commit()
        return jsonify({"message": f"Successfully imported {saved_count} assignments."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)