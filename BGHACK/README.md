# VidyaQuest – Full-Stack STEM Learning Platform

VidyaQuest is an interactive STEM learning platform designed with a modern frontend interface and a robust Python (Flask + SQLite3) backend.

---

## 🚀 Features

- **Frontend**: Responsive Single-Page Application with gamified STEM quizzes, interactive mini-games (Bridge Builder, Slide Puzzle, Memory Match, Rocket Launch, Circuit Connect, Word Warrior), multi-language support (English, Hindi, Tamil, Telugu, Marathi, Kannada), and Text-to-Speech AI Assistant.
- **Python Backend**: Flask REST API integrated with an SQLite3 database (`vidyaquest.db`), handling user authentication (Students, Teachers, Parents), question banks, XP updates, leaderboards, classrooms, and intelligent STEM AI Q&A.

---

## 📁 Project Structure

```text
BGHACK/
├── app.py              # Python Flask REST API Backend & SQLite database manager
├── index.html          # Full-featured interactive HTML5 / JS STEM Frontend
├── vidyaquest.db       # SQLite Database (Auto-generated on server start)
├── requirements.txt    # Python dependencies (Flask, Flask-CORS)
└── README.md           # Documentation
```

---

## 🛠️ Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Python Backend Server
```bash
python app.py
```
The backend server will start on: **`http://localhost:5000`**

### 3. Access the Web Application
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the VidyaQuest Frontend application |
| `/api/auth/register` | `POST` | Registers a new Student, Teacher, or Parent account |
| `/api/auth/login` | `POST` | User login and role verification |
| `/api/student/<username>` | `GET` | Fetches student profile, stats, and subject scores |
| `/api/student/update` | `POST` | Updates student XP, level, streaks, and subject mastery |
| `/api/leaderboard` | `GET` | Retrieves global top-student leaderboard |
| `/api/questions` | `GET` | Fetches question bank grouped by subject |
| `/api/questions/add` | `POST` | Allows teachers to add new STEM questions |
| `/api/questions/<id>` | `DELETE` | Allows teachers to delete questions |
| `/api/ai/chat` | `POST` | Intelligent STEM AI Assistant Q&A response engine |
| `/api/teacher/students` | `GET` | Lists student analytics for teacher dashboards |

---

## 💡 Demo Credentials (Pre-populated)
- **Student Login**: 
  - Username: `rahul`
  - Password: `rahul123@`
