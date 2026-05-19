import requests
import json
from config import Config

class AIDebuggerService:
    """AI-powered debugging service using Groq"""
    
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.api_url = Config.GROQ_API_URL
        self.model = "llama-3.3-70b-versatile" # Using a capable model available on Groq
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _call_groq(self, prompt):
        """Helper to call Groq API"""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 1024
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                raise Exception(f"Groq API Error: {response.text}")
                
        except Exception as e:
            raise Exception(f"Failed to call AI service: {str(e)}")

    def analyze_error(self, code, language, error_message, error_type='runtime'):
        """Analyze code error and provide suggestions"""
        try:
            prompt = f"""You are an expert programming tutor and debugger. A student is learning {language} and encountered an error.

**Code:**
```{language}
{code}
```

**Error Type:** {error_type}
**Error Message:**
```
{error_message}
```

Please provide:
1. **Error Explanation**: Explain what caused this error in simple terms
2. **Fix Suggestion**: Provide specific code fixes or corrections
3. **Learning Tip**: Share a tip to help the student avoid this error in the future

Keep your response clear, concise, and educational. Format your response in markdown."""

            analysis = self._call_groq(prompt)
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error analyzing code: {str(e)}'
            }
    
    def explain_output(self, code, language, output):
        """Explain what the code does and its output"""
        try:
            prompt = f"""You are an expert programming tutor. A student wrote this {language} code and wants to understand it better.

**Code:**
```{language}
{code}
```

**Output:**
```
{output}
```

Please provide:
1. **Code Explanation**: Explain what this code does step-by-step
2. **Output Explanation**: Explain why the output is what it is
3. **Key Concepts**: Highlight the key programming concepts used

Keep your response clear, concise, and educational. Format your response in markdown."""

            explanation = self._call_groq(prompt)
            return {
                'success': True,
                'explanation': explanation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error explaining code: {str(e)}'
            }
    
    def suggest_improvements(self, code, language):
        """Suggest code improvements and best practices"""
        try:
            prompt = f"""You are an expert programming tutor. Review this {language} code and suggest improvements.

**Code:**
```{language}
{code}
```

Please provide:
1. **Code Review**: Brief assessment of the code quality
2. **Improvements**: Specific suggestions to improve the code (performance, readability, best practices)
3. **Improved Code**: Show an improved version of the code if applicable

Keep your response clear, concise, and educational. Format your response in markdown."""

            suggestions = self._call_groq(prompt)
            return {
                'success': True,
                'suggestions': suggestions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error suggesting improvements: {str(e)}'
            }
    
    def generate_test_cases(self, code, language):
        """Generate test cases for the code"""
        try:
            prompt = f"""You are an expert programming tutor. Generate test cases for this {language} code.

**Code:**
```{language}
{code}
```

Please provide:
1. **Test Cases**: 3-5 test cases with inputs and expected outputs
2. **Edge Cases**: Any edge cases to consider
3. **Testing Tips**: Tips for testing this type of code

Keep your response clear and practical. Format your response in markdown."""

            test_cases = self._call_groq(prompt)
            return {
                'success': True,
                'test_cases': test_cases
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generating test cases: {str(e)}'
            }

# Singleton instance
ai_debugger_service = AIDebuggerService()
