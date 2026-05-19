import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
import PyPDF2
import pdfplumber
from config import Config

class RAGService:
    def __init__(self):
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.vector_stores = {}  # course_id -> (index, chunks, metadata)
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with page numbers"""
        chunks = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text and text.strip():
                        chunks.append({
                            'text': text.strip(),
                            'page': page_num,
                            'source': os.path.basename(pdf_path)
                        })
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        if text and text.strip():
                            chunks.append({
                                'text': text.strip(),
                                'page': page_num,
                                'source': os.path.basename(pdf_path)
                            })
            except Exception as e2:
                print(f"Fallback extraction also failed: {e2}")
        
        return chunks
    
    def chunk_text(self, text: str, chunk_size: int = Config.CHUNK_SIZE, 
                   overlap: int = Config.CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def process_documents(self, course_id: str, pdf_paths: List[str]) -> bool:
        """Process PDFs and create vector store for a course"""
        all_chunks = []
        all_metadata = []
        
        # Extract and chunk all documents
        for pdf_path in pdf_paths:
            page_chunks = self.extract_text_from_pdf(pdf_path)
            
            for page_data in page_chunks:
                text_chunks = self.chunk_text(page_data['text'])
                
                for chunk in text_chunks:
                    all_chunks.append(chunk)
                    all_metadata.append({
                        'source': page_data['source'],
                        'page': page_data['page'],
                        'text': chunk
                    })
        
        if not all_chunks:
            print(f"No text extracted from documents for course {course_id}")
            return False
        
        # Generate embeddings
        print(f"Generating embeddings for {len(all_chunks)} chunks...")
        embeddings = self.model.encode(all_chunks, show_progress_bar=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype('float32'))
        
        # Store in memory
        self.vector_stores[course_id] = {
            'index': index,
            'chunks': all_chunks,
            'metadata': all_metadata
        }
        
        # Save to disk
        store_path = os.path.join(Config.VECTOR_STORE_PATH, f"{course_id}.pkl")
        with open(store_path, 'wb') as f:
            pickle.dump({
                'chunks': all_chunks,
                'metadata': all_metadata,
                'embeddings': embeddings
            }, f)
        
        # Save FAISS index
        faiss_path = os.path.join(Config.VECTOR_STORE_PATH, f"{course_id}.index")
        faiss.write_index(index, faiss_path)
        
        print(f"✓ Vector store created for course {course_id} with {len(all_chunks)} chunks")
        return True
    
    def load_vector_store(self, course_id: str) -> bool:
        """Load vector store from disk"""
        if course_id in self.vector_stores:
            print(f"✓ Vector store for course {course_id} already loaded in memory")
            return True
        
        store_path = os.path.join(Config.VECTOR_STORE_PATH, f"{course_id}.pkl")
        faiss_path = os.path.join(Config.VECTOR_STORE_PATH, f"{course_id}.index")
        
        if not os.path.exists(store_path) or not os.path.exists(faiss_path):
            print(f"✗ Vector store files not found for course {course_id}")
            print(f"  Expected: {store_path} and {faiss_path}")
            return False
        
        try:
            print(f"Loading vector store for course {course_id}...")
            with open(store_path, 'rb') as f:
                data = pickle.load(f)
            
            index = faiss.read_index(faiss_path)
            
            self.vector_stores[course_id] = {
                'index': index,
                'chunks': data['chunks'],
                'metadata': data['metadata']
            }
            print(f"✓ Successfully loaded vector store for course {course_id} ({len(data['chunks'])} chunks)")
            return True
        except Exception as e:
            print(f"✗ Error loading vector store for {course_id}: {e}")
            return False
    
    def retrieve(self, course_id: str, query: str, top_k: int = Config.TOP_K_RESULTS) -> List[Dict]:
        """Retrieve relevant chunks for a query"""
        if not self.load_vector_store(course_id):
            return []
        
        store = self.vector_stores[course_id]
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search
        distances, indices = store['index'].search(
            np.array(query_embedding).astype('float32'), 
            top_k
        )
        
        # Format results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(store['metadata']):
                result = store['metadata'][idx].copy()
                result['relevance_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                results.append(result)
        
        return results
    
    def get_context_for_llm(self, course_id: str, query: str, top_k: int = Config.TOP_K_RESULTS) -> Tuple[str, List[Dict]]:
        """Get formatted context and citations for LLM"""
        results = self.retrieve(course_id, query, top_k)
        
        if not results:
            return "", []
        
        # Format context
        context_parts = []
        citations = []
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result['text']}")
            citations.append({
                'number': i,
                'source': result['source'],
                'page': result['page'],
                'relevance': result['relevance_score']
            })
        
        context = "\n\n".join(context_parts)
        return context, citations

# Global instance
rag_service = RAGService()
