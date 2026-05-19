import os
import json
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Firebase Admin SDK - Get credentials as JSON string from environment
    FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS_JSON', '{}')
    
    # Parse Firebase credentials from JSON string
    try:
        FIREBASE_CREDENTIALS = json.loads(FIREBASE_CREDENTIALS_JSON)
    except (json.JSONDecodeError, ValueError):
        FIREBASE_CREDENTIALS = {}
    
    # Google AI
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', '')
    # Groq / OpenAI-compatible API
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    
    # Judge0
    JUDGE0_API_URL = os.getenv('JUDGE0_API_URL', 'https://ce.judge0.com')
    JUDGE0_API_KEY = os.getenv('JUDGE0_API_KEY', '') # Optional for public instance
    
    # RAG Configuration
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K_RESULTS = 5
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'ppt', 'pptx'}
    
    # Vector Store
    VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', 'vector_stores')
