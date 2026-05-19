from typing import Dict
from datetime import datetime, timedelta

class KnowledgeTracker:
    def __init__(self):
        pass
    
    def calculate_mastery(self, topic: str, quiz_scores: list, study_sessions: list) -> float:
        """Calculate mastery level for a topic (0-1 scale)"""
        if not quiz_scores and not study_sessions:
            return 0.0
        
        # Weight recent performance more heavily
        quiz_weight = 0.7
        practice_weight = 0.3
        
        # Calculate quiz-based mastery
        topic_quiz_scores = [
            score for score in quiz_scores 
            if topic in score.get('topics', [])
        ]
        
        if topic_quiz_scores:
            # Use exponential moving average to weight recent scores more
            quiz_mastery = self._exponential_moving_average(
                [s['score'] / 100 for s in topic_quiz_scores]
            )
        else:
            quiz_mastery = 0.5  # Neutral if no quiz data
        
        # Calculate practice-based mastery (based on study time)
        topic_sessions = [
            session for session in study_sessions
            if topic in session.get('topics', [])
        ]
        
        if topic_sessions:
            total_hours = sum(s.get('duration', 0) for s in topic_sessions)
            # Assume 10 hours of study = full mastery from practice
            practice_mastery = min(1.0, total_hours / 10)
        else:
            practice_mastery = 0.0
        
        # Combine scores
        mastery = quiz_weight * quiz_mastery + practice_weight * practice_mastery
        return round(mastery, 3)
    
    def _exponential_moving_average(self, scores: list, alpha: float = 0.3) -> float:
        """Calculate EMA to weight recent scores more heavily"""
        if not scores:
            return 0.0
        
        ema = scores[0]
        for score in scores[1:]:
            ema = alpha * score + (1 - alpha) * ema
        
        return ema
    
    def update_topic_mastery(self, progress_data: Dict, new_quiz_result: Dict) -> Dict:
        """Update mastery levels based on new quiz results"""
        topic_mastery = progress_data.get('topicMastery', {})
        quiz_scores = progress_data.get('quizScores', [])
        study_sessions = progress_data.get('studySessions', [])
        
        # Add new quiz result
        quiz_scores.append(new_quiz_result)
        
        # Recalculate mastery for affected topics
        for topic in new_quiz_result.get('topics', []):
            topic_mastery[topic] = self.calculate_mastery(topic, quiz_scores, study_sessions)
        
        progress_data['topicMastery'] = topic_mastery
        progress_data['quizScores'] = quiz_scores
        progress_data['lastUpdated'] = datetime.utcnow().isoformat()
        
        return progress_data
    
    def log_study_session(self, progress_data: Dict, session: Dict) -> Dict:
        """Log a study session and update mastery"""
        study_sessions = progress_data.get('studySessions', [])
        study_sessions.append(session)
        
        topic_mastery = progress_data.get('topicMastery', {})
        quiz_scores = progress_data.get('quizScores', [])
        
        # Update mastery for studied topics
        for topic in session.get('topics', []):
            topic_mastery[topic] = self.calculate_mastery(topic, quiz_scores, study_sessions)
        
        progress_data['studySessions'] = study_sessions
        progress_data['topicMastery'] = topic_mastery
        progress_data['lastUpdated'] = datetime.utcnow().isoformat()
        
        return progress_data
    
    def get_weak_topics(self, topic_mastery: Dict, threshold: float = 0.6) -> list:
        """Identify topics that need more attention"""
        weak_topics = [
            {'topic': topic, 'mastery': mastery}
            for topic, mastery in topic_mastery.items()
            if mastery < threshold
        ]
        
        # Sort by mastery (lowest first)
        weak_topics.sort(key=lambda x: x['mastery'])
        
        return weak_topics
    
    def get_spaced_repetition_schedule(self, topic: str, mastery: float) -> datetime:
        """Calculate when to review a topic based on mastery"""
        # Higher mastery = longer interval
        if mastery >= 0.9:
            days = 30  # Review in a month
        elif mastery >= 0.7:
            days = 14  # Review in 2 weeks
        elif mastery >= 0.5:
            days = 7   # Review in a week
        else:
            days = 3   # Review in 3 days
        
        return datetime.utcnow() + timedelta(days=days)
    
    def get_analytics(self, progress_data: Dict) -> Dict:
        """Generate progress analytics"""
        topic_mastery = progress_data.get('topicMastery', {})
        quiz_scores = progress_data.get('quizScores', [])
        study_sessions = progress_data.get('studySessions', [])
        
        # Overall mastery
        avg_mastery = sum(topic_mastery.values()) / len(topic_mastery) if topic_mastery else 0
        
        # Quiz statistics
        avg_quiz_score = sum(q['score'] for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        # Study time
        total_study_hours = sum(s.get('duration', 0) for s in study_sessions)
        
        # Weak topics
        weak_topics = self.get_weak_topics(topic_mastery)
        
        # Strong topics
        strong_topics = [
            {'topic': topic, 'mastery': mastery}
            for topic, mastery in topic_mastery.items()
            if mastery >= 0.8
        ]
        strong_topics.sort(key=lambda x: x['mastery'], reverse=True)
        
        return {
            'overall_mastery': round(avg_mastery, 3),
            'average_quiz_score': round(avg_quiz_score, 2),
            'total_study_hours': round(total_study_hours, 2),
            'total_quizzes': len(quiz_scores),
            'total_sessions': len(study_sessions),
            'weak_topics': weak_topics[:5],  # Top 5 weak topics
            'strong_topics': strong_topics[:5],  # Top 5 strong topics
            'topics_count': len(topic_mastery)
        }

# Global instance
knowledge_tracker = KnowledgeTracker()
