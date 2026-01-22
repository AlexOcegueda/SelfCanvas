import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Import your parsers
from importers import parse_mit_assignments, parse_mit_json, parse_text_syllabus

app = Flask(__name__)

# --- CONFIGURATION ---
# Replace with your actual Netlify URL (no trailing slash)
FRONTEND_URL = "https://canvasocegueda.netlify.app" 

app.config['SECRET_KEY'] = 'change-this-to-something-secret' # Needed for session cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Required for cross-site cookies (Netlify -> PythonAnywhere)
app.config['SESSION_COOKIE_SECURE'] = True       # Required for Chrome/modern browsers

# Database Config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'canvas.db')

# CORS Config (MUST enable credentials for cookies to work)
CORS(app, 
     resources={r"/api/*": {"origins": [FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"]}}, 
     supports_credentials=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# --- MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    courses = db.relationship('Course', backref='owner', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Linked to User
    modules = db.relationship('Module', backref='course', cascade="all, delete", lazy=True)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

# --- AUTH HELPER ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AUTH ROUTES ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user) # Auto-login after register
    return jsonify({"message": "Registered successfully", "username": username}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        login_user(user, remember=True)
        return jsonify({"message": "Logged in", "username": user.username})
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})

@app.route('/api/check-session', methods=['GET'])
def check_session():
    if current_user.is_authenticated:
        return jsonify({"is_authenticated": True, "username": current_user.username})
    return jsonify({"is_authenticated": False}), 200

# --- APP ROUTES (Protected) ---

@app.route('/api/course', methods=['GET'])
@login_required
def get_courses():
    # Only show courses belonging to the current user
    courses = Course.query.filter_by(user_id=current_user.id).all()
    output = []
    for course in courses:
        output.append({'id': course.id, 'title': course.title})
    return jsonify(output)

@app.route('/api/courses', methods=['POST'])
@login_required
def create_course():
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title: return jsonify({"error": "Title required"}), 400

    # Link new course to current_user
    new_course = Course(title=title, owner=current_user)
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Created", "course": {"id": new_course.id, "title": new_course.title}}), 201

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
@login_required
def delete_course(course_id):
    # Ensure user owns the course before deleting
    course = Course.query.filter_by(id=course_id, user_id=current_user.id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

@app.route('/api/course/<int:course_id>', methods=['GET'])
@login_required
def get_course_details(course_id):
    # Ensure user owns the course
    course = Course.query.filter_by(id=course_id, user_id=current_user.id).first_or_404()
    modules_list = []
    for module in course.modules:
        modules_list.append({
            "id": module.id,
            "title": module.title,
            "content": module.content,
            "completed": module.completed
        })
    return jsonify({"id": course.id, "title": course.title, "modules": modules_list})

@app.route('/api/upload-mit-assignments', methods=['POST'])
@login_required
def upload_mit_assignments():
    course_id = request.form.get('course_id')
    
    # 1. Security Check: Verify ownership
    course = Course.query.filter_by(id=course_id, user_id=current_user.id).first()
    if not course:
        return jsonify({"error": "Course not found or access denied"}), 403

    # 2. Check Input (File or Text)
    file = request.files.get('file')
    raw_text = request.form.get('raw_text')

    extracted_data = []

    # Path A: File Upload
    if file:
        filename = file.filename.lower()
        content = file.read().decode('utf-8', errors='ignore')
        
        if filename.endswith('.json'):
            extracted_data = parse_mit_json(content)
        elif filename.endswith('.html') or filename.endswith('.htm'):
            extracted_data = parse_mit_assignments(content)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

    # Path B: Text Paste
    elif raw_text:
        extracted_data = parse_text_syllabus(raw_text)

    else:
        return jsonify({"error": "No file or text provided"}), 400

    # Handle Errors from Parser
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

@app.route('/api/modules/<int:module_id>/toggle', methods=['POST'])
@login_required
def toggle_module(module_id):
    module = Module.query.get_or_404(module_id)
    # Security Check: Ensure module belongs to a course owned by current_user
    if module.course.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    module.completed = not module.completed
    db.session.commit()
    return jsonify({"message": "Updated", "completed": module.completed})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)