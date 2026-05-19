from flask import Blueprint, request, jsonify
from routes.auth import verify_token
from firebase_admin import firestore
from services.study_plan_service import study_plan_service
from services.knowledge_tracker import knowledge_tracker

study_plans_bp = Blueprint('study_plans', __name__)
db = firestore.client()

@study_plans_bp.route('/generate', methods=['POST'])
@verify_token
def generate_plan():
    """Generate a personalized study plan"""
    try:
        data = request.get_json()
        
        course_id = data.get('courseId')
        hours_per_week = data.get('hoursPerWeek', 10)
        target_weeks = data.get('targetWeeks', 12)
        priorities = data.get('priorities', [])
        
        # Get course data
        course_doc = db.collection('courses').document(course_id).get()
        
        if not course_doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = course_doc.to_dict()
        
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate study plan
        plan = study_plan_service.generate_study_plan(
            course_title=course_data.get('title', 'Course'),
            syllabus=course_data.get('syllabus', ''),
            hours_per_week=hours_per_week,
            target_weeks=target_weeks,
            priorities=priorities
        )
        
        # Save to Firestore
        plan_data = {
            'userId': request.user_id,
            'courseId': course_id,
            'weeks': plan['weeks'],
            'constraints': {
                'hoursPerWeek': hours_per_week,
                'targetDate': None,
                'priorities': priorities
            },
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('study_plans').document()
        doc_ref.set(plan_data)
        
        plan_data['id'] = doc_ref.id
        
        return jsonify(plan_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_plans_bp.route('/<course_id>', methods=['GET'])
@verify_token
def get_plan(course_id):
    """Get study plan for a course"""
    try:
        plans_ref = db.collection('study_plans').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        plans = []
        for doc in plans_ref.stream():
            plan_data = doc.to_dict()
            plan_data['id'] = doc.id
            plans.append(plan_data)
        
        if not plans:
            return jsonify({'error': 'No study plan found'}), 404
        
        # Return the most recent plan
        plans.sort(key=lambda x: x.get('createdAt', 0), reverse=True)
        
        return jsonify(plans[0]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_plans_bp.route('/<plan_id>', methods=['PUT'])
@verify_token
def update_plan(plan_id):
    """Update study plan (e.g., mark tasks as completed)"""
    try:
        doc_ref = db.collection('study_plans').document(plan_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Study plan not found'}), 404
        
        plan_data = doc.to_dict()
        
        if plan_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        update_data = {
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        if 'weeks' in data:
            update_data['weeks'] = data['weeks']
        
        doc_ref.update(update_data)
        
        return jsonify({'message': 'Study plan updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@study_plans_bp.route('/<plan_id>/adjust', methods=['POST'])
@verify_token
def adjust_plan(plan_id):
    """Auto-adjust study plan based on progress"""
    try:
        # Get study plan
        plan_doc = db.collection('study_plans').document(plan_id).get()
        
        if not plan_doc.exists:
            return jsonify({'error': 'Study plan not found'}), 404
        
        plan_data = plan_doc.to_dict()
        
        if plan_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get progress data
        course_id = plan_data.get('courseId')
        progress_ref = db.collection('progress').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        progress_data = {}
        for doc in progress_ref.stream():
            progress_data = doc.to_dict()
            break
        
        # Adjust plan
        adjusted_plan = study_plan_service.adjust_plan(plan_data, progress_data)
        
        # Update in Firestore
        db.collection('study_plans').document(plan_id).update({
            'weeks': adjusted_plan['weeks'],
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'message': 'Study plan adjusted successfully',
            'plan': adjusted_plan
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
