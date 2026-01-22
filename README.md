# SelfCanvas: The LMS for Autodidacts

**Live Demo:** [https://canvasocegueda.netlify.app](https://canvasocegueda.netlify.app)

*(Try the "One-Click Guest Login" to test it instantly!)*

**

## 💡 The Problem

The internet gives us access to world-class education (MIT OpenCourseWare, Coursera, YouTube), but it lacks **infrastructure**.

* MIT OCW gives you a folder of PDFs and HTML files, but no way to track what you've finished.
* Self-studiers often quit because they lack the "Dashboard" experience of a university LMS (like Canvas or Blackboard) that visualizes progress.

## 🚀 The Solution

**SelfCanvas** is a custom-built Learning Management System designed to turn static open-courseware files into tracked, interactive courses. It features a **custom ingestion engine** that parses raw HTML syllabi and converts them into a structured database of modules, quizzes, and readings with progress tracking.

## 🛠️ Tech Stack

### Frontend

* **Framework:** SvelteKit (Static Adapter / SPA Mode)
* **Language:** TypeScript
* **Styling:** Tailwind CSS (v4)
* **Hosting:** Netlify

### Backend

* **Framework:** Flask (Python)
* **Database:** SQLite (via SQLAlchemy)
* **Authentication:** Flask-Login (Session-based with HttpOnly cookies)
* **Hosting:** PythonAnywhere

---

## ✨ Key Features

### 1. Dual-Pipeline Ingestion Engine

I built a custom parsing algorithm in Python that accepts unstructured data and standardizes it into learning modules:

* **HTML Pipeline:** Scrapes `downloads/index.html` or `calendar.html` files from MIT OpenCourseWare zips, identifying rows, dates, and resource links.
* **Text Pipeline:** Uses RegEx to parse pasted text from Coursera or edX syllabi into checklist items.

### 2. Optimistic UI Updates

To ensure the app feels native and snappy, the frontend updates the UI state (checkboxes, progress bars) **immediately** upon user interaction, while the network request processes in the background.

### 3. Secure Cross-Origin Authentication

Since the Frontend (Netlify) and Backend (PythonAnywhere) live on different domains, I implemented a strict CORS policy allowing secure credentials (`Access-Control-Allow-Credentials`) to pass HttpOnly session cookies for persistent login states.

---

## 📖 How to Use (Demo Mode)

Recruiters and visitors can test the full functionality without creating an account:

1. **Login:** Click the **"One-Click Guest Login"** button on the login page.
2. **Create a Course:** Click "Add New Course" (e.g., "Linear Algebra").
3. **Import Data:** Click into the course and select the **"MIT File Upload"** tab.
4. **Click Filepath:** navigate to {course_name}/download/index.html, and click.
* Upload that file back into the dropzone.
* Watch the parsing engine generate the course modules instantly.



---

## 🔧 Local Setup

If you want to run this locally:

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/SelfCanvas.git
cd SelfCanvas

```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
python app.py

```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev

```

### 4. Configuration

Ensure your `backend/app.py` has the CORS origin set to localhost:

```python
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}}, supports_credentials=True)

```
