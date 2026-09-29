# Resume AI - Python FastAPI Backend

This is the FastAPI backend for Resume AI, powered by **FastAPI**, **Uvicorn**, **SQLAlchemy ORM**, **MySQL**, **Pydantic v2**, and **Google Gemini AI**.

---

## 🚀 Features

- **Framework**: FastAPI with asynchronous request handling and high-throughput Uvicorn ASGI server.
- **ORM & Database**: SQLAlchemy with MySQL, featuring automated database creation (`CREATE DATABASE IF NOT EXISTS`) and table migrations.
- **Data Validation**: Strict Pydantic v2 schemas for all requests and responses with appropriate HTTP status codes (200, 201, 400, 401, 404, 500).
- **Authentication**: JWT token authentication with bcrypt password hashing, HttpOnly cookie support (with Bearer header fallback), and token blacklisting on logout.
- **Resume Parsing**: Text extraction from uploaded PDF resumes using `pypdf`.
- **AI Integration**: Structured interview analysis and strategy generation with Google Gemini API via the official `google-genai` SDK.
- **Resume PDF Generation**: ATS-friendly HTML-to-PDF conversion powered by Playwright headless Chromium.

---

## 🛠️ Prerequisites

1. **Python**: 3.10+ installed
2. **MySQL Workbench / Server**: Running locally on port `3306`

---

## ⚙️ Environment Variables (.env)

Create or update the `.env` file in the `Backend/` directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173

# MySQL Database Details (from MySQL Workbench)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_workbench_password
MYSQL_DATABASE=resume_ai_db

# JWT Authentication
JWT_SECRET=super_secret_jwt_key_please_change_in_production_xyz123
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=1

# Google Gemini API
GOOGLE_GENAI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

---

## 🔑 How to Get a Google Gemini API Key from Google AI Studio

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google Account.
3. Click on the **"Get API key"** button on the left sidebar (or top right).
4. Click **"Create API key"**.
5. Select an existing Google Cloud project or choose **"Create API key in new project"**.
6. Copy the generated API key string (e.g. `AIzaSy...`).
7. Paste it into your `Backend/.env` file under `GOOGLE_GENAI_API_KEY`:
   ```env
   GOOGLE_GENAI_API_KEY=AIzaSyYourGeneratedKeyHere
   ```

---

## 📦 Installation & Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Chromium (for PDF resume generation)**:
   ```bash
   playwright install chromium
   ```

3. **Start the FastAPI server**:
   ```bash
   python run.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Interactive API Documentation**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🗄️ MySQL Database Structure

The application automatically creates the database and the following tables in MySQL upon startup:

1. `users`: Stores user credentials (`id`, `username`, `email`, `password`, `created_at`, `updated_at`).
2. `blacklist_tokens`: Stores invalidated JWT tokens on user logout.
3. `interview_reports`: Stores job descriptions, candidate resumes, self-descriptions, match scores, and JSON arrays of technical questions, behavioral questions, skill gaps, and preparation roadmaps.
