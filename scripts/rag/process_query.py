#!/usr/bin/env python3.8
"""
US-004 Step 2: Query Processing Pipeline
Process user queries, generate embeddings, and search vector database
"""

import sys
import os
import json
import numpy as np
import pickle
from datetime import datetime

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def load_vector_database():
    """Load the vector database from US-003"""
    log_message("Loading vector database from US-003...")
    
    try:
        # Import required libraries
        import faiss
        from sentence_transformers import SentenceTransformer
        
        # Database paths from US-003
        db_dir = "/opt/rag-copilot/db"
        index_file = os.path.join(db_dir, "vector_db.index")
        metadata_file = os.path.join(db_dir, "vector_db_metadata.json")
        chunks_file = os.path.join(db_dir, "chunks_backup.pkl")
        
        # Load FAISS index
        if not os.path.exists(index_file):
            log_message(f"❌ Vector database not found: {index_file}", "ERROR")
            return None, None, None
        
        index = faiss.read_index(index_file)
        log_message(f"✅ FAISS index loaded: {index.ntotal} vectors")
        
        # Load metadata
        metadata = {}
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            log_message(f"✅ Database metadata loaded")
        
        # Load document chunks
        chunks = None
        if os.path.exists(chunks_file):
            with open(chunks_file, 'rb') as f:
                chunks = pickle.load(f)
            log_message(f"✅ Document chunks loaded: {len(chunks)} chunks")
        
        # Load embedding model (same as US-003)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        log_message(f"✅ Embedding model loaded")
        
        return index, chunks, model
        
    except Exception as e:
        log_message(f"❌ Failed to load vector database: {str(e)}", "ERROR")
        return None, None, None

def preprocess_query(query_text):
    """Preprocess user query"""
    log_message(f"Preprocessing query: {query_text[:50]}...")
    
    try:
        # Basic text cleaning
        processed_query = query_text.strip()
        
        # Remove excessive whitespace
        processed_query = ' '.join(processed_query.split())
        
        # Basic validation
        if len(processed_query) < 3:
            log_message("⚠️  Query too short (< 3 characters)", "WARNING")
        
        if len(processed_query) > 1000:
            log_message("⚠️  Query too long (> 1000 characters), truncating", "WARNING")
            processed_query = processed_query[:1000]
        
        # Detect language (simple heuristic)
        vietnamese_chars = set('àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹđ')
        has_vietnamese = any(char.lower() in vietnamese_chars for char in processed_query)
        language = "vietnamese" if has_vietnamese else "english"
        
        log_message(f"✅ Query preprocessed")
        log_message(f"   Length: {len(processed_query)} characters")
        log_message(f"   Language: {language}")
        
        return processed_query, language
        
    except Exception as e:
        log_message(f"❌ Query preprocessing failed: {str(e)}", "ERROR")
        return None, None

def generate_query_embedding(query_text, model):
    """Generate embedding for the query"""
    log_message("Generating query embedding...")
    
    try:
        # Generate embedding using same model as US-003
        embedding = model.encode([query_text])
        
        log_message(f"✅ Query embedding generated")
        log_message(f"   Shape: {embedding.shape}")
        log_message(f"   Dimension: {embedding.shape[1]}")
        
        return embedding
        
    except Exception as e:
        log_message(f"❌ Embedding generation failed: {str(e)}", "ERROR")
        return None

def search_vector_database(index, query_embedding, k=5):
    """Search vector database for similar documents"""
    log_message(f"Searching vector database for top {k} results...")
    
    try:
        # Ensure query embedding is correct format
        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)
        
        # Perform similarity search
        distances, indices = index.search(query_embedding, k)
        
        log_message(f"✅ Vector search completed")
        log_message(f"   Results found: {len(indices[0])}")
        log_message(f"   Top distances: {distances[0][:3]}")
        
        return distances[0], indices[0]
        
    except Exception as e:
        log_message(f"❌ Vector search failed: {str(e)}", "ERROR")
        return None, None

def format_search_results(distances, indices, chunks, query_text):
    """Format search results with relevance scores"""
    log_message("Formatting search results...")
    
    try:
        results = []
        
        for i, (distance, idx) in enumerate(zip(distances, indices)):
            # Convert distance to similarity score
            similarity_score = 1 / (1 + distance)
            
            result = {
                'rank': i + 1,
                'document_index': int(idx),
                'similarity_score': float(similarity_score),
                'distance': float(distance),
                'content': None,
                'metadata': None
            }
            
            # Add document content if available
            if chunks and idx < len(chunks):
                chunk = chunks[idx]
                if isinstance(chunk, dict):
                    result['content'] = chunk.get('content', str(chunk))
                    result['metadata'] = {k: v for k, v in chunk.items() if k != 'content'}
                else:
                    result['content'] = str(chunk)
            
            results.append(result)
        
        log_message(f"✅ Search results formatted: {len(results)} results")
        
        return results
        
    except Exception as e:
        log_message(f"❌ Result formatting failed: {str(e)}", "ERROR")
        return []

def save_query_results(query_text, language, results, output_file=None):
    """Save query processing results"""
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"/tmp/query_results_{timestamp}.json"
    
    log_message(f"Saving query results to: {output_file}")
    
    try:
        query_data = {
            'query': query_text,
            'language': language,
            'timestamp': datetime.now().isoformat(),
            'total_results': len(results),
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(query_data, f, indent=2, ensure_ascii=False)
        
        log_message(f"✅ Query results saved")
        return output_file
        
    except Exception as e:
        log_message(f"❌ Failed to save results: {str(e)}", "ERROR")
        return None

def main():
    """Main query processing function"""
    log_message("=== US-004 STEP 2: QUERY PROCESSING PIPELINE ===")
    
    # Check command line arguments
    if len(sys.argv) != 2:
        log_message("Usage: python3.8 process_query.py <query_text>", "ERROR")
        log_message("Example: python3.8 process_query.py \"What are the best AI coding tools?\"", "ERROR")
        sys.exit(1)
    
    query_text = sys.argv[1]
    
    # Step 1: Load vector database and models
    index, chunks, model = load_vector_database()
    if index is None:
        log_message("❌ Failed to load vector database components", "ERROR")
        sys.exit(1)
    
    # Step 2: Preprocess query
    processed_query, language = preprocess_query(query_text)
    if processed_query is None:
        log_message("❌ Query preprocessing failed", "ERROR")
        sys.exit(1)
    
    # Step 3: Generate query embedding
    query_embedding = generate_query_embedding(processed_query, model)
    if query_embedding is None:
        log_message("❌ Embedding generation failed", "ERROR")
        sys.exit(1)
    
    # Step 4: Search vector database
    distances, indices = search_vector_database(index, query_embedding, k=5)
    if distances is None:
        log_message("❌ Vector search failed", "ERROR")
        sys.exit(1)
    
    # Step 5: Format results
    results = format_search_results(distances, indices, chunks, processed_query)
    if not results:
        log_message("❌ No results found or formatting failed", "ERROR")
        sys.exit(1)
    
    # Step 6: Save results
    output_file = save_query_results(processed_query, language, results)
    
    # Step 7: Display results
    print("\n" + "="*80)
    print(f"🔍 QUERY PROCESSING RESULTS")
    print("="*80)
    print(f"Query: {processed_query}")
    print(f"Language: {language}")
    print(f"Results found: {len(results)}")
    print()
    
    for result in results[:3]:  # Show top 3
        print(f"📄 RESULT #{result['rank']}")
        print(f"   Similarity Score: {result['similarity_score']:.4f}")
        print(f"   Content: {result['content'][:150]}...")
        print("-" * 60)
    
    # Success summary
    log_message("=== STEP 2 COMPLETED SUCCESSFULLY ===")
    log_message(f"✅ Query processed: {processed_query}")
    log_message(f"✅ Language detected: {language}")
    log_message(f"✅ Embedding generated: {query_embedding.shape}")
    log_message(f"✅ Vector search completed: {len(results)} results")
    log_message(f"✅ Results saved: {output_file}")
    log_message("")
    log_message("🚀 Ready for Step 3: Context Retrieval & Ranking")

if __name__ == "__main__":
    main() 