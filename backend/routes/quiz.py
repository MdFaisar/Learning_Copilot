from flask import Blueprint, request, jsonify
from routes.auth import verify_token
from firebase_admin import firestore
from services.quiz_service import quiz_service
from services.knowledge_tracker import knowledge_tracker
from services.rag_service import rag_service

quiz_bp = Blueprint('quiz', __name__)
db = firestore.client()

@quiz_bp.route('/generate', methods=['POST'])
@verify_token
def generate_quiz():
    """Generate an adaptive quiz"""
    try:
        data = request.get_json()
        
        course_id = data.get('courseId')
        topics = data.get('topics', [])
        # Default topic if none provided to prevent backend crash
        if not topics:
            topics = ['General Knowledge']
        num_questions = data.get('numQuestions', 5)
        
        # Get course data
        course_doc = db.collection('courses').document(course_id).get()
        
        if not course_doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = course_doc.to_dict()
        
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get progress to determine difficulty
        progress_ref = db.collection('progress').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        progress_data = {}
        for doc in progress_ref.stream():
            progress_data = doc.to_dict()
            break
        
        # Calculate average mastery for topics
        topic_mastery = progress_data.get('topicMastery', {})
        avg_mastery = 0.5  # Default
        
        if topics and topic_mastery:
            relevant_mastery = [topic_mastery.get(t, 0.5) for t in topics]
            avg_mastery = sum(relevant_mastery) / len(relevant_mastery)
        
        # Determine difficulty
        difficulty = quiz_service.get_adaptive_difficulty(avg_mastery)
        
        # Get context from RAG if available
        context = ""
        if topics:
            try:
                context_text, _ = rag_service.get_context_for_llm(course_id, f"Generate quiz questions about {', '.join(topics)}", top_k=3)
                context = context_text
            except:
                pass
        
        # Generate quiz
        quiz_data = quiz_service.generate_quiz(
            course_id=course_id,
            topics=topics,
            difficulty=difficulty,
            num_questions=num_questions,
            context=context
        )
        
        # Save to Firestore
        quiz_record = {
            'userId': request.user_id,
            'courseId': course_id,
            'questions': quiz_data['questions'],
            'difficulty': difficulty,
            'topics': topics,
            'createdAt': datetime.utcnow()
        }
        
        doc_ref = db.collection('quiz_history').document()
        doc_ref.set(quiz_record)
        
        quiz_data['id'] = doc_ref.id
        
        return jsonify(quiz_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import traceback
from datetime import datetime

@quiz_bp.route('/submit', methods=['POST'])
@verify_token
def submit_quiz():
    """Submit quiz answers and get results"""
    try:
        data = request.get_json()
        
        quiz_id = data.get('quizId')
        questions = data.get('questions', [])
        course_id = data.get('courseId')
        
        # Evaluate quiz
        results = quiz_service.evaluate_quiz(questions)
        
        # Update quiz record
        db.collection('quiz_history').document(quiz_id).update({
            'questions': questions,
            'score': results['score'],
            'completedAt': datetime.utcnow()
        })
        
        # Update progress
        # Using filter kwarg or standard where clauses. usage of positional args is fine but might warn.
        # We ensure to catch errors.
        progress_ref = db.collection('progress').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        progress_doc_id = None
        progress_data = {}
        
        for doc in progress_ref.stream():
            progress_doc_id = doc.id
            progress_data = doc.to_dict()
            break
        
        # Create progress document if it doesn't exist
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
        
        # Update mastery
        quiz_result = {
            'quizId': quiz_id,
            'score': results['score'],
            'completedAt': datetime.utcnow(), # Use standard datetime
            'topics': list(results['topic_mastery'].keys())
        }
        
        updated_progress = knowledge_tracker.update_topic_mastery(progress_data, quiz_result)
        
        # Save updated progress
        db.collection('progress').document(progress_doc_id).set(updated_progress)
        
        return jsonify({
            'results': results,
            'questions': questions,
            'updated_mastery': updated_progress.get('topicMastery', {})
        }), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/history/<course_id>', methods=['GET'])
@verify_token
def get_quiz_history(course_id):
    """Get quiz history for a course"""
    try:
        quizzes_ref = db.collection('quiz_history').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        quizzes = []
        for doc in quizzes_ref.stream():
            quiz_data = doc.to_dict()
            quiz_data['id'] = doc.id
            quizzes.append(quiz_data)
        
        # Sort by creation date
        quizzes.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        return jsonify(quizzes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
