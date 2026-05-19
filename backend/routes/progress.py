from flask import Blueprint, request, jsonify
from routes.auth import verify_token
from firebase_admin import firestore
from services.knowledge_tracker import knowledge_tracker
from datetime import datetime

progress_bp = Blueprint('progress', __name__)
db = firestore.client()

@progress_bp.route('/<course_id>', methods=['GET'])
@verify_token
def get_progress(course_id):
    """Get progress for a course"""
    try:
        progress_ref = db.collection('progress').where(
            filter=firestore.FieldFilter('courseId', '==', course_id)
        ).where(
            filter=firestore.FieldFilter('userId', '==', request.user_id)
        )
        
        for doc in progress_ref.stream():
            progress_data = doc.to_dict()
            progress_data['id'] = doc.id
            
            # Get analytics
            analytics = knowledge_tracker.get_analytics(progress_data)
            progress_data['analytics'] = analytics
            
            return jsonify(progress_data), 200
        
        # No progress yet
        return jsonify({
            'courseId': course_id,
            'topicMastery': {},
            'quizScores': [],
            'studySessions': [],
            'analytics': {
                'overall_mastery': 0,
                'average_quiz_score': 0,
                'total_study_hours': 0,
                'total_quizzes': 0,
                'total_sessions': 0,
                'weak_topics': [],
                'strong_topics': [],
                'topics_count': 0
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/session', methods=['POST'])
@verify_token
def log_session():
    """Log a study session"""
    try:
        data = request.get_json()
        
        course_id = data.get('courseId')
        duration = data.get('duration', 0)  # in hours
        topics = data.get('topics', [])
        
        # Get or create progress document
        progress_ref = db.collection('progress').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        progress_doc_id = None
        progress_data = {}
        
        for doc in progress_ref.stream():
            progress_doc_id = doc.id
            progress_data = doc.to_dict()
            break
        
        if not progress_doc_id:
            progress_data = {
                'userId': request.user_id,
                'courseId': course_id,
                'topicMastery': {},
                'quizScores': [],
                'studySessions': []
            }
            progress_doc_ref = db.collection('progress').document()
            progress_doc_ref.set(progress_data)
            progress_doc_id = progress_doc_ref.id
        
        # Log session
        session = {
            'date': datetime.utcnow(),
            'duration': duration,
            'topics': topics
        }
        
        updated_progress = knowledge_tracker.log_study_session(progress_data, session)
        
        # Save
        db.collection('progress').document(progress_doc_id).set(updated_progress)
        
        return jsonify({
            'message': 'Study session logged successfully',
            'updated_mastery': updated_progress.get('topicMastery', {})
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@progress_bp.route('/mastery', methods=['PUT'])
@verify_token
def update_mastery():
    """Manually update topic mastery (for testing/admin)"""
    try:
        data = request.get_json()
        
        course_id = data.get('courseId')
        topic = data.get('topic')
        mastery = data.get('mastery', 0)
        
        # Get progress document
        progress_ref = db.collection('progress').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        progress_doc_id = None
        progress_data = {}
        
        for doc in progress_ref.stream():
            progress_doc_id = doc.id
            progress_data = doc.to_dict()
            break
        
        if not progress_doc_id:
            return jsonify({'error': 'No progress data found'}), 404
        
        # Update mastery
        topic_mastery = progress_data.get('topicMastery', {})
        topic_mastery[topic] = mastery
        
        db.collection('progress').document(progress_doc_id).update({
            'topicMastery': topic_mastery,
            'lastUpdated': datetime.utcnow()
        })
        
        return jsonify({
            'message': 'Mastery updated successfully',
            'topic': topic,
            'mastery': mastery
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
