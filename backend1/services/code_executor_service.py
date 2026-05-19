import requests
import time
from config import Config

class CodeExecutorService:
    """Service for executing code using Judge0 API"""
    
    # Popular language mappings to Judge0 language IDs
    # Based on https://ce.judge0.com/languages
    LANGUAGE_MAP = {
        'python': 71,      # Python (3.8.1)
        'javascript': 63,  # JavaScript (Node.js 12.14.0)
        'java': 62,        # Java (OpenJDK 13.0.1)
        'c': 50,           # C (GCC 9.2.0)
        'cpp': 54,         # C++ (GCC 9.2.0)
        'csharp': 51,      # C# (Mono 6.6.0.161)
        'ruby': 72,        # Ruby (2.7.0)
        'go': 60,          # Go (1.13.5)
        'rust': 73,        # Rust (1.40.0)
        'php': 68,         # PHP (7.4.1)
        'swift': 83,       # Swift (5.2.3)
        'kotlin': 78,      # Kotlin (1.3.70)
        'typescript': 74,  # TypeScript (3.7.4)
    }
    
    def __init__(self):
        self.api_url = Config.JUDGE0_API_URL
        self.api_key = Config.JUDGE0_API_KEY
        self.headers = {
            'Content-Type': 'application/json'
        }
        # Add API Key if present (for RapidAPI or self-hosted auth)
        if self.api_key:
             # RapidAPI specific headers if using RapidAPI
             if 'rapidapi' in self.api_url:
                 self.headers['X-RapidAPI-Key'] = self.api_key
                 self.headers['X-RapidAPI-Host'] = 'judge0-ce.p.rapidapi.com'
             else:
                 pass

    def get_language_id(self, language_name):
        """Get Judge0 language ID from language name"""
        return self.LANGUAGE_MAP.get(language_name.lower())
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        # Return static list for UI stability and consistency with frontend icons
        return [
            {'name': 'Python', 'value': 'python', 'id': 71},
            {'name': 'JavaScript', 'value': 'javascript', 'id': 63},
            {'name': 'Java', 'value': 'java', 'id': 62},
            {'name': 'C', 'value': 'c', 'id': 50},
            {'name': 'C++', 'value': 'cpp', 'id': 54},
            {'name': 'C#', 'value': 'csharp', 'id': 51},
            {'name': 'Ruby', 'value': 'ruby', 'id': 72},
            {'name': 'Go', 'value': 'go', 'id': 60},
            {'name': 'Rust', 'value': 'rust', 'id': 73},
            {'name': 'PHP', 'value': 'php', 'id': 68},
            {'name': 'Swift', 'value': 'swift', 'id': 83},
            {'name': 'Kotlin', 'value': 'kotlin', 'id': 78},
            {'name': 'TypeScript', 'value': 'typescript', 'id': 74},
        ]
    
    def execute_code(self, language, source_code, stdin=''):
        """Execute code using Judge0"""
        try:
            language_id = self.get_language_id(language)
            if not language_id:
                return {'error': f'Unsupported language: {language}'}
            
            payload = {
                'language_id': language_id,
                'source_code': source_code,
                'stdin': stdin
            }
            
            # Using ?wait=true as per user instructions
            url = f'{self.api_url}/submissions?wait=true&base64_encoded=false'
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code in [200, 201]:
                return self._format_result(response.json())
            else:
                 return {'error': f'Submission failed: {response.text}'}
                
        except Exception as e:
            return {'error': f'Error executing code: {str(e)}'}
    
    def _format_result(self, result):
        """Format Judge0 result for frontend"""
        status = result.get('status', {})
        
        formatted = {
            'status': status.get('description', 'Unknown'),
            'status_id': status.get('id'),
            'stdout': result.get('stdout', ''),
            'stderr': result.get('stderr', ''),
            'compile_output': result.get('compile_output', ''),
            'message': result.get('message', ''),
            'time': result.get('time', '0'),
            'memory': result.get('memory', '0'),
        }
        
        # Determine if there was an error
        # Status IDs: 6=Compilation Error, 7-12=Runtime Errors, 13=Internal Error
        if status.get('id') == 6:
            formatted['error'] = result.get('compile_output', 'Compilation failed')
        elif status.get('id') in [7, 8, 9, 10, 11, 12]:
            formatted['error'] = result.get('stderr', 'Runtime error occurred')
        elif status.get('id') == 13:
             formatted['error'] = 'Internal error occurred'
        
        return formatted

# Singleton instance
code_executor_service = CodeExecutorService()
