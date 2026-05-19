from flask import Blueprint, request, jsonify
from services.code_executor_service import code_executor_service
from services.ai_debugger_service import ai_debugger_service

code_editor_bp = Blueprint('code_editor', __name__)

@code_editor_bp.route('/languages', methods=['GET'])
def get_languages():
    """Get list of supported programming languages"""
    try:
        languages = code_executor_service.get_supported_languages()
        return jsonify({
            'success': True,
            'languages': languages
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_editor_bp.route('/execute', methods=['POST'])
def execute_code():
    """Execute code and return results"""
    try:
        data = request.get_json()
        
        language = data.get('language')
        source_code = data.get('code')
        stdin = data.get('input', '')
        
        if not language or not source_code:
            return jsonify({
                'success': False,
                'error': 'Language and code are required'
            }), 400
        
        # Execute code
        result = code_executor_service.execute_code(language, source_code, stdin)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 200
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_editor_bp.route('/debug', methods=['POST'])
def debug_code():
    """Analyze code errors using AI"""
    try:
        data = request.get_json()
        
        code = data.get('code')
        language = data.get('language')
        error_message = data.get('error')
        error_type = data.get('errorType', 'runtime')
        
        if not code or not language or not error_message:
            return jsonify({
                'success': False,
                'error': 'Code, language, and error message are required'
            }), 400
        
        # Analyze error with AI
        analysis = ai_debugger_service.analyze_error(code, language, error_message, error_type)
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_editor_bp.route('/explain', methods=['POST'])
def explain_code():
    """Explain code and output using AI"""
    try:
        data = request.get_json()
        
        code = data.get('code')
        language = data.get('language')
        output = data.get('output', '')
        
        if not code or not language:
            return jsonify({
                'success': False,
                'error': 'Code and language are required'
            }), 400
        
        # Explain code with AI
        explanation = ai_debugger_service.explain_output(code, language, output)
        
        return jsonify(explanation), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_editor_bp.route('/improve', methods=['POST'])
def improve_code():
    """Get code improvement suggestions using AI"""
    try:
        data = request.get_json()
        
        code = data.get('code')
        language = data.get('language')
        
        if not code or not language:
            return jsonify({
                'success': False,
                'error': 'Code and language are required'
            }), 400
        
        # Get improvement suggestions with AI
        suggestions = ai_debugger_service.suggest_improvements(code, language)
        
        return jsonify(suggestions), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@code_editor_bp.route('/test-cases', methods=['POST'])
def generate_test_cases():
    """Generate test cases for code using AI"""
    try:
        data = request.get_json()
        
        code = data.get('code')
        language = data.get('language')
        
        if not code or not language:
            return jsonify({
                'success': False,
                'error': 'Code and language are required'
            }), 400
        
        # Generate test cases with AI
        test_cases = ai_debugger_service.generate_test_cases(code, language)
        
        return jsonify(test_cases), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
