from flask import Blueprint, request, jsonify
from routes.auth import verify_token
from firebase_admin import firestore, storage
from services.rag_service import rag_service
from werkzeug.utils import secure_filename
import os
from config import Config
from datetime import datetime

courses_bp = Blueprint('courses', __name__)
db = firestore.client()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@courses_bp.route('', methods=['GET'])
@verify_token
def get_courses():
    """Get all courses for the authenticated user"""
    try:
        courses_ref = db.collection('courses').where(
            filter=firestore.FieldFilter('userId', '==', request.user_id)
        )
        courses = []
        
        for doc in courses_ref.stream():
            course_data = doc.to_dict()
            course_data['id'] = doc.id
            courses.append(course_data)
        
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('', methods=['POST'])
@verify_token
def create_course():
    """Create a new course"""
    try:
        data = request.get_json()
        
        course_data = {
            'userId': request.user_id,
            'title': data.get('title'),
            'description': data.get('description', ''),
            'syllabus': data.get('syllabus', ''),
            'materials': [],
            'processingStatus': None,  # None, 'pending', 'processing', 'completed', 'failed'
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('courses').document()
        doc_ref.set(course_data)
        
        course_data['id'] = doc_ref.id
        # Replace Firestore Sentinel with serializable date for response
        course_data['createdAt'] = datetime.utcnow().isoformat()
        course_data['updatedAt'] = datetime.utcnow().isoformat()
        
        return jsonify(course_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_id>', methods=['GET'])
@verify_token
def get_course(course_id):
    """Get a specific course"""
    try:
        doc = db.collection('courses').document(course_id).get()
        
        if not doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = doc.to_dict()
        
        # Verify ownership
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        course_data['id'] = doc.id
        return jsonify(course_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_id>', methods=['PUT'])
@verify_token
def update_course(course_id):
    """Update a course"""
    try:
        doc_ref = db.collection('courses').document(course_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = doc.to_dict()
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        update_data = {
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        if 'title' in data:
            update_data['title'] = data['title']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'syllabus' in data:
            update_data['syllabus'] = data['syllabus']
        
        doc_ref.update(update_data)
        
        return jsonify({'message': 'Course updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_id>', methods=['DELETE'])
@verify_token
def delete_course(course_id):
    """Delete a course"""
    try:
        doc_ref = db.collection('courses').document(course_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = doc.to_dict()
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        doc_ref.delete()
        
        return jsonify({'message': 'Course deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_id>/materials', methods=['POST'])
@verify_token
def upload_material(course_id):
    """Upload course material"""
    try:
        # Verify course ownership
        doc_ref = db.collection('courses').document(course_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = doc.to_dict()
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{course_id}_{timestamp}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        file.save(filepath)
        
        # Update course materials
        material_data = {
            'name': filename,
            'type': filename.rsplit('.', 1)[1].lower(),
            'url': filepath,
            'uploadedAt': datetime.utcnow().isoformat()
        }
        
        materials = course_data.get('materials', [])
        materials.append(material_data)
        
        doc_ref.update({
            'materials': materials,
            'processingStatus': 'pending',
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'message': 'Material uploaded successfully',
            'material': material_data
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<course_id>/process', methods=['POST'])
@verify_token
def process_materials(course_id):
    """Process and index course materials for RAG"""
    try:
        # Verify course ownership
        doc_ref = db.collection('courses').document(course_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = doc.to_dict()
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get PDF materials
        materials = course_data.get('materials', [])
        pdf_paths = [m['url'] for m in materials if m['type'] == 'pdf']
        
        if not pdf_paths:
            return jsonify({'error': 'No PDF materials to process'}), 400
        
        # Update status to processing
        doc_ref.update({
            'processingStatus': 'processing',
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        # Process documents
        print(f"Processing {len(pdf_paths)} PDF files for course {course_id}...")
        success = rag_service.process_documents(course_id, pdf_paths)
        
        if success:
            # Update status to completed
            doc_ref.update({
                'processingStatus': 'completed',
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            print(f"✓ Successfully processed materials for course {course_id}")
            return jsonify({
                'message': 'Materials processed successfully',
                'processed_files': len(pdf_paths)
            }), 200
        else:
            # Update status to failed
            doc_ref.update({
                'processingStatus': 'failed',
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            print(f"✗ Failed to process materials for course {course_id}")
            return jsonify({'error': 'Failed to process materials'}), 500
    except Exception as e:
        # Update status to failed on exception
        try:
            doc_ref.update({
                'processingStatus': 'failed',
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
        except:
            pass
        print(f"✗ Error processing materials for course {course_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
