from flask import Blueprint, request, jsonify
from routes.auth import verify_token
from firebase_admin import firestore
from services.rag_service import rag_service
from services.llm_client import generate_content
from config import Config

qa_bp = Blueprint('qa', __name__)
db = firestore.client()


@qa_bp.route('/query', methods=['POST'])
@verify_token
def query():
    """Answer question using RAG"""
    try:
        data = request.get_json()
        
        course_id = data.get('courseId')
        question = data.get('question')
        
        # Validate required fields
        if not course_id:
            return jsonify({'error': 'Course ID is required'}), 400
            
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Verify course access
        course_doc = db.collection('courses').document(course_id).get()
        
        if not course_doc.exists:
            return jsonify({'error': 'Course not found'}), 404
        
        course_data = course_doc.to_dict()
        
        if course_data.get('userId') != request.user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if materials have been processed
        processing_status = course_data.get('processingStatus')
        if processing_status != 'completed':
            status_msg = {
                'pending': 'Course materials have not been processed yet. Please process the materials first.',
                'processing': 'Course materials are currently being processed. Please wait a moment and try again.',
                'failed': 'Course material processing failed. Please try processing the materials again.',
                None: 'No course materials have been uploaded or processed yet.'
            }.get(processing_status, 'Course materials are not ready for Q&A.')
            
            return jsonify({'error': status_msg}), 400
        
        # Retrieve relevant context
        context, citations = rag_service.get_context_for_llm(course_id, question, top_k=5)
        
        if not context:
            return jsonify({
                'error': 'Could not find relevant information in the course materials. The vector store may be corrupted. Try reprocessing the materials.'
            }), 500
        
        prompt = f"""
        You are a helpful teaching assistant. Answer the student's question based on the provided course materials.
        
        Question: {question}
        
        Relevant course materials:
        {context}
        
        Instructions:
        - Provide a clear, educational answer
        - Reference the source materials using [1], [2], etc.
        - If the materials don't fully answer the question, acknowledge this
        - Be concise but thorough
        - Use examples when helpful
        """
        
        # Use Groq/OpenAI-compatible model
        model_name = 'openai/gpt-oss-120b'
        answer = generate_content(prompt, model=model_name, max_tokens=1024)
        
        # Save to conversation history (optional)
        qa_record = {
            'userId': request.user_id,
            'courseId': course_id,
            'question': question,
            'answer': answer,
            'citations': citations,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        
        db.collection('qa_history').document().set(qa_record)
        
        return jsonify({
            'answer': answer,
            'citations': citations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qa_bp.route('/history/<course_id>', methods=['GET'])
@verify_token
def get_history(course_id):
    """Get Q&A history for a course"""
    try:
        qa_ref = db.collection('qa_history').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        history = []
        for doc in qa_ref.stream():
            qa_data = doc.to_dict()
            qa_data['id'] = doc.id
            history.append(qa_data)
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@qa_bp.route('/history/<course_id>/clear', methods=['DELETE'])
@verify_token
def clear_history(course_id):
    """Clear Q&A history for a course"""
    try:
        print(f"Adding request to clear history for course {course_id} by user {request.user_id}")
        
        # Reference to valid documents
        qa_ref = db.collection('qa_history').where('courseId', '==', course_id).where('userId', '==', request.user_id)
        
        deleted_count = 0
        batch_size = 400
        
        while True:
            # Get a batch of documents
            docs = list(qa_ref.limit(batch_size).stream())
            if not docs:
                break
            
            print(f"Deleting batch of {len(docs)} messages...")
            batch = db.batch()
            for doc in docs:
                batch.delete(doc.reference)
            batch.commit()
            
            deleted_count += len(docs)
            
        print(f"✓ Successfully cleared {deleted_count} messages for course {course_id}")
        return jsonify({'message': f'Q&A history cleared ({deleted_count} messages deleted)'}), 200
        
    except Exception as e:
        print(f"✗ Error clearing history: {str(e)}")
        return jsonify({'error': str(e)}), 500
