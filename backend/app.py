from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from importers import parse_mit_assignments, parse_mit_json, parse_text_syllabus

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://canvasocegueda.netlify.app"}})
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
    completed = db.Column(db.Boolean, default=False)

# --- ROUTES ---

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    output = []
    for course in courses:
        output.append({'id': course.id, 'title': course.title})
    return jsonify(output)

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
        
    title = data['title'].strip()
    if not title:
         return jsonify({"error": "Title cannot be empty"}), 400

    try:
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

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    try:
        # Delete modules first
        Module.query.filter_by(course_id=course_id).delete()
        # Delete course
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Course deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 2. UPDATE get_course_details TO SEND THE STATUS
@app.route('/api/course/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    course = Course.query.get_or_404(course_id)
    modules_list = []
    for module in course.modules:
        modules_list.append({
            "id": module.id,
            "title": module.title,
            "content": module.content,
            "completed": module.completed 
        })
    return jsonify({
        "id": course.id,
        "title": course.title,
        "modules": modules_list
    })

# 3. NEW ROUTE TO TOGGLE COMPLETION
@app.route('/api/modules/<int:module_id>/toggle', methods=['POST'])
def toggle_module(module_id):
    module = Module.query.get_or_404(module_id)
    
    # Flip the status (True -> False, False -> True)
    module.completed = not module.completed
    
    try:
        db.session.commit()
        return jsonify({"message": "Updated", "completed": module.completed})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- THE COMBINED UPLOAD ROUTE ---
@app.route('/api/upload-mit-assignments', methods=['POST'])
def upload_mit_assignments():
    course_id = request.form.get('course_id')
    
    # Check for File OR Text
    file = request.files.get('file')
    raw_text = request.form.get('raw_text')

    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400

    extracted_data = []

    # 1. Handle File Upload (MIT HTML/JSON)
    if file:
        filename = file.filename.lower()
        content = file.read().decode('utf-8', errors='ignore')
        
        if filename.endswith('.json'):
            extracted_data = parse_mit_json(content)
        elif filename.endswith('.html') or filename.endswith('.htm'):
            extracted_data = parse_mit_assignments(content)
        else:
            return jsonify({"error": "Unsupported file type. Please upload .html or .json"}), 400

    # 2. Handle Text Paste (Coursera/edX)
    elif raw_text:
        print(f"Processing Text Paste for Course {course_id}")
        extracted_data = parse_text_syllabus(raw_text)

    else:
        return jsonify({"error": "No file or text provided"}), 400

    if isinstance(extracted_data, dict) and "error" in extracted_data:
        return jsonify(extracted_data), 400
    
    if not extracted_data:
        return jsonify({"message": "Parsed but found 0 items."}), 200

    # 3. Save to DB
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
        return jsonify({"message": f"Successfully imported {saved_count} items."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)