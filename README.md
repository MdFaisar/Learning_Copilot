# Personalized Learning Copilot

An AI-powered learning assistant that helps students plan, track, and master core courses through personalized study roadmaps, intelligent Q&A with RAG, adaptive quizzes, and knowledge tracking.

## Features

- 🎯 **Personalized Study Plans**: AI-generated week-by-week roadmaps tailored to your schedule and goals
- 💬 **Intelligent Q&A**: Ask questions and get answers from your course materials using RAG (Retrieval-Augmented Generation)
- 📊 **Progress Tracking**: Monitor your mastery levels and identify areas for improvement
- ✅ **Adaptive Quizzes**: Practice with questions that match your skill level
- 📚 **Course Management**: Upload and organize course materials (PDFs, slides)
- 🔐 **Google Authentication**: Secure login with Google OAuth

## Tech Stack

### Frontend
- **React** (Vite) - Modern UI framework
- **React Router** - Client-side routing
- **Firebase** - Authentication and Firestore database
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icons

### Backend
- **Flask** - Python web framework
- **Firebase Admin SDK** - Server-side Firebase integration
- **Sentence Transformers** - Text embeddings for RAG
- **FAISS** - Vector similarity search
- **Google Gemini AI** - Text generation for study plans and quizzes
- **PyPDF2/pdfplumber** - PDF processing

### Deployment
- **Render** - Backend hosting
- **Firebase Hosting** or **Vercel** - Frontend hosting

## Project Structure

```
Anti_2/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   ├── Procfile              # Render deployment config
│   ├── services/
│   │   ├── rag_service.py    # RAG pipeline
│   │   ├── study_plan_service.py  # Study plan generation
│   │   ├── quiz_service.py   # Quiz generation
│   │   └── knowledge_tracker.py   # Progress tracking
│   └── routes/
│       ├── auth.py           # Authentication endpoints
│       ├── courses.py        # Course management
│       ├── study_plans.py    # Study plan endpoints
│       ├── quiz.py           # Quiz endpoints
│       ├── qa.py             # Q&A endpoints
│       └── progress.py       # Progress tracking
│
└── frontend/
    ├── src/
    │   ├── components/       # Reusable components
    │   ├── contexts/         # React contexts
    │   ├── pages/            # Page components
    │   ├── services/         # API client
    │   ├── config/           # Firebase config
    │   ├── App.jsx           # Main app component
    │   └── main.jsx          # Entry point
    ├── package.json
    └── vite.config.js
```

## Setup Instructions

### Prerequisites
- **Node.js** (v18+)
- **Python** (v3.9+)
- **Firebase Project** (for authentication and database)
- **Google AI API Key** (for Gemini)

### 1. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable **Google Authentication**:
   - Go to Authentication → Sign-in method
   - Enable Google provider
4. Create a **Firestore Database**:
   - Go to Firestore Database → Create database
   - Start in production mode
5. Enable **Storage**:
   - Go to Storage → Get started
6. Get your Firebase config:
   - Go to Project Settings → General
   - Scroll to "Your apps" → Web app
   - Copy the configuration
7. Generate a service account key:
   - Go to Project Settings → Service accounts
   - Click "Generate new private key"
   - Save as `firebase-credentials.json` in the `backend/` directory

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env and add your credentials:
# - GOOGLE_AI_API_KEY (from Google AI Studio)
# - FIREBASE_CREDENTIALS_PATH (path to your firebase-credentials.json)
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
copy .env.example .env

# Edit .env and add your Firebase config:
# VITE_FIREBASE_API_KEY=your-api-key
# VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
# VITE_FIREBASE_PROJECT_ID=your-project-id
# VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
# VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
# VITE_FIREBASE_APP_ID=your-app-id
# VITE_API_URL=http://localhost:5000/api
```

### 4. Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate on Mac/Linux
python app.py
```

Backend will run on `http://localhost:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

## Deployment

### Backend Deployment (Render)

1. Create a new Web Service on [Render](https://render.com/)
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**:
     - `GOOGLE_AI_API_KEY`
     - `FIREBASE_CREDENTIALS_PATH` (upload firebase-credentials.json as a secret file)
     - `ALLOWED_ORIGINS` (your frontend URL)
4. Deploy

### Frontend Deployment (Vercel)

1. Install Vercel CLI: `npm install -g vercel`
2. Run `vercel` in the frontend directory
3. Add environment variables in Vercel dashboard
4. Update `VITE_API_URL` to your Render backend URL

## Usage Guide

### 1. Create a Course
1. Login with Google
2. Click "Add Course" on the dashboard
3. Enter course title, description, and syllabus
4. Click "Create Course"

### 2. Upload Materials
1. Go to course detail page
2. Click "Upload PDF" to add course materials
3. Click "Process Materials for Q&A" to enable RAG

### 3. Generate Study Plan
1. On the course detail page, click "Generate Study Plan"
2. The AI will create a personalized week-by-week roadmap
3. View and track your progress in the Study Plan page

### 4. Take Quizzes
1. Go to the Quiz page
2. Select a course
3. Click "Generate Quiz"
4. Answer questions and submit
5. View results and explanations

### 5. Ask Questions
1. Go to the Q&A page or course detail page
2. Type your question
3. Get AI-powered answers with citations from course materials

### 6. Track Progress
1. Go to the Progress page
2. View your overall mastery, quiz scores, and study hours
3. Identify weak topics that need more attention

## Color Palette

The application uses a professional color scheme:
- **White** (#FFFFFF) - Primary background
- **Gray** (#F3F4F6 - #111827) - Text and neutral elements
- **Orange** (#F97316) - Primary actions and highlights
- **Black** (#000000) - High contrast text
- **Green** (#22C55E) - Success states and mastery indicators

## API Documentation

### Authentication
- `POST /api/auth/verify` - Verify Firebase token

### Courses
- `GET /api/courses` - List user's courses
- `POST /api/courses` - Create new course
- `GET /api/courses/:id` - Get course details
- `PUT /api/courses/:id` - Update course
- `DELETE /api/courses/:id` - Delete course
- `POST /api/courses/:id/materials` - Upload course material
- `POST /api/courses/:id/process` - Process and index materials

### Study Plans
- `POST /api/study-plans/generate` - Generate personalized study plan
- `GET /api/study-plans/:courseId` - Get study plan for course
- `PUT /api/study-plans/:id` - Update study plan
- `POST /api/study-plans/:id/adjust` - Auto-adjust based on progress

### Quiz
- `POST /api/quiz/generate` - Generate adaptive quiz
- `POST /api/quiz/submit` - Submit quiz answers
- `GET /api/quiz/history/:courseId` - Get quiz history

### Q&A (RAG)
- `POST /api/qa/query` - Ask question with RAG retrieval
- `GET /api/qa/history/:courseId` - Get Q&A history

### Progress
- `GET /api/progress/:courseId` - Get progress for course
- `POST /api/progress/session` - Log study session
- `PUT /api/progress/mastery` - Update topic mastery

## Troubleshooting

### Backend Issues

**Error: Firebase Admin initialization failed**
- Ensure `firebase-credentials.json` is in the correct location
- Check that `FIREBASE_CREDENTIALS_PATH` in `.env` is correct

**Error: Google AI API key invalid**
- Get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Update `GOOGLE_AI_API_KEY` in `.env`

**Error: Module not found**
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Frontend Issues

**Error: Firebase configuration invalid**
- Check all Firebase environment variables in `.env`
- Ensure no trailing spaces or quotes

**Error: Network request failed**
- Check that backend is running
- Verify `VITE_API_URL` points to correct backend URL
- Check CORS configuration in backend

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please create an issue on GitHub.
