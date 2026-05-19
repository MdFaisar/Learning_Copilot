from config import Config
from services.llm_client import generate_content
from typing import List, Dict
import re

class StudyPlanService:
    def __init__(self):
        # model name for Groq / OpenAI-compatible API
        self.model_name = 'openai/gpt-oss-120b'

    def parse_syllabus(self, syllabus_text: str) -> List[str]:
        """Extract topics from syllabus"""
        prompt = f"""
        Extract the main topics from this course syllabus. Return only a numbered list of topics.
        
        Syllabus:
        {syllabus_text}
        
        Format: Return each topic on a new line as: 1. Topic Name
        """
        
        try:
            response_text = generate_content(prompt, model=self.model_name)
            topics = []
            for line in response_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                    # Remove numbering and bullet points
                    topic = re.sub(r'^[\d\.\-\*\s]+', '', line).strip()
                    if topic:
                        topics.append(topic)
            return topics
        except Exception as e:
            print(f"Error parsing syllabus: {e}")
            # Fallback: simple line splitting
            return [line.strip() for line in syllabus_text.split('\n') if line.strip()]
    
    def generate_study_plan(self, course_title: str, syllabus: str, 
                          hours_per_week: int, target_weeks: int,
                          priorities: List[str] = None) -> Dict:
        """Generate personalized study plan"""
        
        topics = self.parse_syllabus(syllabus)
        
        prompt = f"""
        Create a detailed {target_weeks}-week study plan for a course titled "{course_title}".
        
        Topics to cover:
        {chr(10).join(f"- {topic}" for topic in topics)}
        
        Constraints:
        - Student can study {hours_per_week} hours per week
        - Must complete in {target_weeks} weeks
        {f"- Priority topics: {', '.join(priorities)}" if priorities else ""}
        
        For each week, provide:
        1. Week number
        2. Topics to cover (2-4 topics per week)
        3. Specific tasks (3-5 tasks per week)
        4. Estimated hours for each task
        5. Learning goals for the week
        
        Format your response as:
        Week N:
        Topics: topic1, topic2
        Tasks:
        - Task description (X hours)
        - Task description (X hours)
        Goals: Brief description of what student should achieve
        
        Make sure tasks are specific, actionable, and time estimates are realistic.
        """
        
        try:
            plan_text = generate_content(prompt, model=self.model_name, max_tokens=1024)
            
            # Parse the response into structured format
            weeks = self._parse_plan_text(plan_text, hours_per_week)
            
            return {
                'weeks': weeks,
                'total_weeks': target_weeks,
                'hours_per_week': hours_per_week,
                'topics': topics
            }
        except Exception as e:
            print(f"Error generating study plan: {e}")
            # Fallback: create basic plan
            return self._create_fallback_plan(topics, target_weeks, hours_per_week)
    
    def _parse_plan_text(self, plan_text: str, hours_per_week: int) -> List[Dict]:
        """Parse AI-generated plan text into structured format"""
        weeks = []
        current_week = None
        
        lines = plan_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detect week header
            if re.match(r'^Week\s+\d+', line, re.IGNORECASE):
                if current_week:
                    weeks.append(current_week)
                
                week_num = int(re.search(r'\d+', line).group())
                current_week = {
                    'weekNumber': week_num,
                    'topics': [],
                    'tasks': [],
                    'goals': ''
                }
            
            elif current_week:
                # Parse topics
                if line.lower().startswith('topics:'):
                    topics_text = line.split(':', 1)[1].strip()
                    current_week['topics'] = [t.strip() for t in topics_text.split(',')]
                
                # Parse tasks
                elif line.startswith('-') or line.startswith('*'):
                    task_text = line.lstrip('-*').strip()
                    # Extract hours if mentioned
                    hours_match = re.search(r'\((\d+(?:\.\d+)?)\s*hours?\)', task_text, re.IGNORECASE)
                    hours = float(hours_match.group(1)) if hours_match else 2.0
                    
                    # Remove hours from task description
                    task_desc = re.sub(r'\(\d+(?:\.\d+)?\s*hours?\)', '', task_text).strip()
                    
                    current_week['tasks'].append({
                        'title': task_desc[:100],  # Limit length
                        'description': task_desc,
                        'estimatedHours': hours,
                        'completed': False
                    })
                
                # Parse goals
                elif line.lower().startswith('goals:'):
                    current_week['goals'] = line.split(':', 1)[1].strip()
        
        # Add last week
        if current_week:
            weeks.append(current_week)
        
        return weeks
    
    def _create_fallback_plan(self, topics: List[str], weeks: int, hours_per_week: int) -> Dict:
        """Create a basic fallback plan if AI generation fails"""
        topics_per_week = max(1, len(topics) // weeks)
        plan_weeks = []
        
        for week_num in range(1, weeks + 1):
            start_idx = (week_num - 1) * topics_per_week
            end_idx = min(start_idx + topics_per_week, len(topics))
            week_topics = topics[start_idx:end_idx]
            
            tasks = []
            hours_per_topic = hours_per_week / max(1, len(week_topics))
            
            for topic in week_topics:
                tasks.append({
                    'title': f'Study {topic}',
                    'description': f'Read and understand {topic} from course materials',
                    'estimatedHours': hours_per_topic * 0.6,
                    'completed': False
                })
                tasks.append({
                    'title': f'Practice {topic}',
                    'description': f'Complete practice problems for {topic}',
                    'estimatedHours': hours_per_topic * 0.4,
                    'completed': False
                })
            
            plan_weeks.append({
                'weekNumber': week_num,
                'topics': week_topics,
                'tasks': tasks,
                'goals': f'Master {", ".join(week_topics)}'
            })
        
        return {
            'weeks': plan_weeks,
            'total_weeks': weeks,
            'hours_per_week': hours_per_week,
            'topics': topics
        }
    
    def adjust_plan(self, current_plan: Dict, progress_data: Dict) -> Dict:
        """Adjust study plan based on progress"""
        # Calculate completion rate
        total_tasks = sum(len(week['tasks']) for week in current_plan['weeks'])
        completed_tasks = sum(
            sum(1 for task in week['tasks'] if task.get('completed', False))
            for week in current_plan['weeks']
        )
        
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        # Identify weak topics from progress data
        weak_topics = []
        if 'topicMastery' in progress_data:
            for topic, mastery in progress_data['topicMastery'].items():
                if mastery < 0.6:  # Less than 60% mastery
                    weak_topics.append(topic)
        
        # Add review tasks for weak topics
        if weak_topics and completion_rate > 0.5:
            # Find upcoming weeks
            for week in current_plan['weeks']:
                if not all(task.get('completed', False) for task in week['tasks']):
                    # Add review task
                    week['tasks'].insert(0, {
                        'title': f'Review: {weak_topics[0]}',
                        'description': f'Additional practice and review for {weak_topics[0]}',
                        'estimatedHours': 1.5,
                        'completed': False
                    })
                    weak_topics.pop(0)
                    if not weak_topics:
                        break
        
        return current_plan

# Global instance
study_plan_service = StudyPlanService()
