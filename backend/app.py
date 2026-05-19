from flask import Flask
from flask_cors import CORS
from config import Config
import firebase_admin
from firebase_admin import credentials
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS configuration
    # CORS configuration
    # Allow all origins for development to prevent Network Errors
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize Firebase Admin
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS_PATH'])
            firebase_admin.initialize_app(cred)
        print("✓ Firebase Admin initialized successfully")
    except Exception as e:
        print(f"⚠ Firebase Admin initialization failed: {e}")
        print("  The app will run but Firebase features won't work.")
    
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VECTOR_STORE_PATH'], exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.courses import courses_bp
    from routes.study_plans import study_plans_bp
    from routes.quiz import quiz_bp
    from routes.qa import qa_bp
    from routes.progress import progress_bp
    from routes.code_editor import code_editor_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(courses_bp, url_prefix='/api/courses')
    app.register_blueprint(study_plans_bp, url_prefix='/api/study-plans')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(qa_bp, url_prefix='/api/qa')
    app.register_blueprint(progress_bp, url_prefix='/api/progress')
    app.register_blueprint(code_editor_bp, url_prefix='/api/code')
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Learning Copilot API is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
