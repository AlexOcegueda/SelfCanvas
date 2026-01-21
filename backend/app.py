from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from importers import parse_mit_assignments 

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canvas.db'
db = SQLAlchemy(app)

# --- MODELS ---
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # This relationship links modules to this course
    modules = db.relationship('Module', backref='course', lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    content = db.Column(db.Text, nullable=True) # Stores the assignment text

# --- ROUTES ---
@app.route('/api/course/<int:course_id>', methods=['GET'])
def get_course_details(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Get all modules associated with this course
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

@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    output = []
    for course in courses:
        output.append({'id': course.id, 'title': course.title})
    return jsonify(output)

@app.route('/api/upload-mit-assignments', methods=['POST'])
def upload_mit_assignments():
    course_id = request.form.get('course_id')
    file = request.files.get('file')

    if not file or not course_id:
        return jsonify({"error": "Missing file or course_id"}), 400

    # Read and parse
    content = file.read().decode('utf-8', errors='ignore')
    extracted_data = parse_mit_assignments(content)

    if "error" in extracted_data:
        return jsonify(extracted_data), 400

    try:
        saved_count = 0
        for item in extracted_data:
            # Check for duplicates
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