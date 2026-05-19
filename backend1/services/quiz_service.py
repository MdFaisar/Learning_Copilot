from config import Config
from services.llm_client import generate_content
from typing import List, Dict
import random

class QuizService:
    def __init__(self):
        self.model_name = 'openai/gpt-oss-120b'
    
    def generate_quiz(self, course_id: str, topics: List[str], 
                     difficulty: float, num_questions: int = 5,
                     context: str = "") -> Dict:
        """Generate adaptive quiz based on topics and difficulty"""
        
        difficulty_desc = self._get_difficulty_description(difficulty)
        
        prompt = f"""
        Generate {num_questions} multiple-choice questions for a quiz on the following topics:
        {chr(10).join(f"- {topic}" for topic in topics)}
        
        Difficulty level: {difficulty_desc} (0-1 scale: {difficulty:.2f})
        
        {f"Use this context from course materials:{chr(10)}{context}" if context else ""}
        
        For each question, provide:
        1. Question text
        2. Four options (A, B, C, D)
        3. Correct answer (letter)
        4. Brief explanation
        5. Topic it covers
        
        Format each question as:
        Q1: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct: [Letter]
        Explanation: [Brief explanation]
        Topic: [Topic name]
        
        Make questions clear, unambiguous, and appropriate for the difficulty level.
        """
        
        try:
            response_text = generate_content(prompt, model=self.model_name, max_tokens=1024)
            questions = self._parse_quiz_response(response_text, topics, difficulty)
            
            return {
                'questions': questions,
                'total_questions': len(questions),
                'difficulty': difficulty,
                'topics': topics
            }
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._create_fallback_quiz(topics, difficulty, num_questions)
    
    def _get_difficulty_description(self, difficulty: float) -> str:
        """Convert difficulty score to description"""
        if difficulty < 0.3:
            return "Easy - Basic recall and understanding"
        elif difficulty < 0.6:
            return "Medium - Application and analysis"
        else:
            return "Hard - Synthesis and evaluation"
    
    def _parse_quiz_response(self, response_text: str, topics: List[str], difficulty: float) -> List[Dict]:
        """Parse AI-generated quiz into structured format"""
        questions = []
        current_question = {}
        options = []
        
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # New question
            if line.startswith('Q') and ':' in line:
                if current_question and 'question' in current_question:
                    current_question['options'] = options
                    questions.append(current_question)
                
                current_question = {
                    'question': line.split(':', 1)[1].strip(),
                    'difficulty': difficulty
                }
                options = []
            
            # Options
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option_text = line[2:].strip()
                options.append(option_text)
            
            # Correct answer
            elif line.lower().startswith('correct:'):
                answer_letter = line.split(':', 1)[1].strip().upper()[0]
                answer_index = ord(answer_letter) - ord('A')
                if 0 <= answer_index < len(options):
                    current_question['correctAnswer'] = options[answer_index]
                    current_question['userAnswer'] = None
            
            # Explanation
            elif line.lower().startswith('explanation:'):
                current_question['explanation'] = line.split(':', 1)[1].strip()
            
            # Topic
            elif line.lower().startswith('topic:'):
                topic = line.split(':', 1)[1].strip()
                current_question['topic'] = topic if topic in topics else topics[0]
        
        # Add last question
        if current_question and 'question' in current_question:
            current_question['options'] = options
            questions.append(current_question)
        
        return questions
    
    def _create_fallback_quiz(self, topics: List[str], difficulty: float, num_questions: int) -> Dict:
        """Create basic fallback quiz if AI generation fails"""
        questions = []
        
        for i in range(num_questions):
            topic = topics[i % len(topics)]
            questions.append({
                'question': f'What is an important concept in {topic}?',
                'options': [
                    f'Concept A related to {topic}',
                    f'Concept B related to {topic}',
                    f'Concept C related to {topic}',
                    f'Concept D related to {topic}'
                ],
                'correctAnswer': f'Concept A related to {topic}',
                'userAnswer': None,
                'topic': topic,
                'difficulty': difficulty,
                'explanation': 'This is a placeholder question. Please upload course materials for better questions.'
            })
        
        return {
            'questions': questions,
            'total_questions': len(questions),
            'difficulty': difficulty,
            'topics': topics
        }
    
    def evaluate_quiz(self, questions: List[Dict]) -> Dict:
        """Evaluate quiz and calculate score"""
        total = len(questions)
        correct = sum(1 for q in questions if q.get('userAnswer') == q.get('correctAnswer'))
        score = (correct / total * 100) if total > 0 else 0
        
        # Topic-wise performance
        topic_performance = {}
        for q in questions:
            topic = q.get('topic', 'Unknown')
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            
            topic_performance[topic]['total'] += 1
            if q.get('userAnswer') == q.get('correctAnswer'):
                topic_performance[topic]['correct'] += 1
        
        # Calculate mastery per topic
        topic_mastery = {}
        for topic, perf in topic_performance.items():
            topic_mastery[topic] = perf['correct'] / perf['total'] if perf['total'] > 0 else 0
        
        return {
            'score': score,
            'correct': correct,
            'total': total,
            'topic_performance': topic_performance,
            'topic_mastery': topic_mastery
        }
    
    def get_adaptive_difficulty(self, mastery_score: float) -> float:
        """Calculate next quiz difficulty based on mastery"""
        # If mastery is high, increase difficulty
        # If mastery is low, decrease difficulty
        if mastery_score >= 0.8:
            return min(0.9, mastery_score + 0.1)
        elif mastery_score >= 0.6:
            return mastery_score
        else:
            return max(0.2, mastery_score - 0.1)

# Global instance
quiz_service = QuizService()
