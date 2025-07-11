#!/usr/bin/env python3.8
"""
US-003 Step 5: Query vector database with similarity search
Search for similar documents using FAISS vector database
"""

import faiss
import json
import pickle
import numpy as np
import os
import sys
import time
from datetime import datetime
from sentence_transformers import SentenceTransformer

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def load_vector_database(db_dir):
    """Load FAISS vector database and metadata"""
    log_message(f"Loading vector database from: {db_dir}")
    
    try:
        # Load FAISS index
        index_file = os.path.join(db_dir, "vector_db.index")
        if not os.path.exists(index_file):
            log_message(f"❌ Index file not found: {index_file}", "ERROR")
            return None, None, None
        
        index = faiss.read_index(index_file)
        log_message(f"✅ FAISS index loaded")
        
        # Load metadata
        metadata_file = os.path.join(db_dir, "vector_db_metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            log_message(f"✅ Database metadata loaded")
        else:
            metadata = {}
            log_message(f"⚠️  No metadata file found", "WARNING")
        
        # Load chunks backup if available
        chunks_file = os.path.join(db_dir, "chunks_backup.pkl")
        if os.path.exists(chunks_file):
            with open(chunks_file, 'rb') as f:
                chunks = pickle.load(f)
            log_message(f"✅ Document chunks loaded")
        else:
            chunks = None
            log_message(f"⚠️  No chunks backup found", "WARNING")
        
        log_message(f"   - Index type: {metadata.get('index_type', 'Unknown')}")
        log_message(f"   - Total vectors: {index.ntotal}")
        log_message(f"   - Dimension: {metadata.get('dimension', 'Unknown')}")
        
        return index, metadata, chunks
    except Exception as e:
        log_message(f"❌ Failed to load vector database: {str(e)}", "ERROR")
        return None, None, None

def initialize_embedding_model():
    """Initialize the same embedding model used for indexing"""
    log_message("Initializing embedding model...")
    
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        log_message("✅ Embedding model loaded")
        log_message(f"   - Model: all-MiniLM-L6-v2")
        log_message(f"   - Embedding dimension: {model.get_sentence_embedding_dimension()}")
        
        return model
    except Exception as e:
        log_message(f"❌ Failed to load embedding model: {str(e)}", "ERROR")
        return None

def search_similar_documents(index, query_embedding, k=5):
    """Search for similar documents using FAISS"""
    log_message(f"Searching for top {k} similar documents...")
    
    try:
        # Ensure query is float32 and correct shape
        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)
        
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Perform search
        start_time = time.time()
        distances, indices = index.search(query_embedding, k)
        search_time = time.time() - start_time
        
        log_message(f"✅ Search completed in {search_time:.4f} seconds")
        log_message(f"   - Query shape: {query_embedding.shape}")
        log_message(f"   - Results found: {len(indices[0])}")
        
        return distances[0], indices[0], search_time
    except Exception as e:
        log_message(f"❌ Search failed: {str(e)}", "ERROR")
        return None, None, None

def format_search_results(distances, indices, chunks, query_text, max_content_length=200):
    """Format search results for display"""
    log_message("Formatting search results...")
    
    try:
        results = []
        
        for i, (distance, idx) in enumerate(zip(distances, indices)):
            result = {
                'rank': i + 1,
                'document_index': int(idx),
                'similarity_score': float(1 / (1 + distance)),  # Convert distance to similarity
                'distance': float(distance),
                'content': None,
                'metadata': None
            }
            
            # Add document content if available
            if chunks and idx < len(chunks):
                chunk = chunks[idx]
                if isinstance(chunk, dict):
                    content = chunk.get('content', chunk.get('text', str(chunk)))
                    result['content'] = content[:max_content_length] + "..." if len(content) > max_content_length else content
                    result['metadata'] = {k: v for k, v in chunk.items() if k not in ['content', 'text']}
                else:
                    content = str(chunk)
                    result['content'] = content[:max_content_length] + "..." if len(content) > max_content_length else content
            
            results.append(result)
        
        log_message(f"✅ Formatted {len(results)} search results")
        return results
    except Exception as e:
        log_message(f"❌ Failed to format results: {str(e)}", "ERROR")
        return []

def display_search_results(results, query_text):
    """Display search results in a readable format"""
    print("\n" + "="*80)
    print(f"🔍 SEARCH QUERY: {query_text}")
    print("="*80)
    
    if not results:
        print("❌ No results found")
        return
    
    for result in results:
        print(f"\n📄 RESULT #{result['rank']}")
        print(f"   Document Index: {result['document_index']}")
        print(f"   Similarity Score: {result['similarity_score']:.4f}")
        print(f"   Distance: {result['distance']:.4f}")
        
        if result['content']:
            print(f"   Content: {result['content']}")
        
        if result['metadata']:
            print(f"   Metadata: {result['metadata']}")
        
        print("-" * 60)

def save_search_results(results, query_text, output_file):
    """Save search results to JSON file"""
    log_message(f"Saving search results to: {output_file}")
    
    try:
        search_data = {
            'query': query_text,
            'timestamp': datetime.now().isoformat(),
            'total_results': len(results),
            'results': results
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, indent=2, ensure_ascii=False)
        
        log_message(f"✅ Search results saved")
        return True
    except Exception as e:
        log_message(f"❌ Failed to save results: {str(e)}", "ERROR")
        return False

def main():
    """Main query processing"""
    log_message("=== US-003 STEP 5: QUERY VECTOR DATABASE ===")
    
    # Check command line arguments
    if len(sys.argv) < 2:
        log_message("Usage: python3.8 query_vector_db.py <query_text> [--timing] [--save-results]", "ERROR")
        log_message("Example: python3.8 query_vector_db.py \"AI coding tools for developers\" --timing", "ERROR")
        sys.exit(1)
    
    # Parse arguments
    query_text = sys.argv[1]
    timing_mode = "--timing" in sys.argv
    save_results = "--save-results" in sys.argv
    
    # Set database directory
    db_dir = "/opt/rag-copilot/db"
    
    # Validate database directory
    if not os.path.exists(db_dir):
        log_message(f"❌ Database directory not found: {db_dir}", "ERROR")
        log_message("Please run Step 4 first to create the vector database", "ERROR")
        sys.exit(1)
    
    log_message(f"Query: {query_text}")
    if timing_mode:
        log_message("Timing mode enabled - will measure performance")
    
    total_start_time = time.time()
    
    # Step 1: Load vector database
    index, metadata, chunks = load_vector_database(db_dir)
    if index is None:
        log_message("❌ Failed to load vector database", "ERROR")
        sys.exit(1)
    
    # Step 2: Initialize embedding model
    model = initialize_embedding_model()
    if model is None:
        log_message("❌ Failed to initialize embedding model", "ERROR")
        sys.exit(1)
    
    # Step 3: Generate query embedding
    log_message("Generating query embedding...")
    try:
        query_embedding = model.encode([query_text])
        log_message(f"✅ Query embedding generated")
        log_message(f"   - Query embedding shape: {query_embedding.shape}")
    except Exception as e:
        log_message(f"❌ Failed to generate query embedding: {str(e)}", "ERROR")
        sys.exit(1)
    
    # Step 4: Search similar documents
    k = min(5, index.ntotal)  # Get top 5 or all available
    distances, indices, search_time = search_similar_documents(index, query_embedding, k)
    if distances is None:
        log_message("❌ Search failed", "ERROR")
        sys.exit(1)
    
    # Step 5: Format and display results
    results = format_search_results(distances, indices, chunks, query_text)
    display_search_results(results, query_text)
    
    # Step 6: Save results if requested
    if save_results:
        output_file = f"/opt/rag-copilot/output/search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_search_results(results, query_text, output_file)
    
    total_time = time.time() - total_start_time
    
    # Performance summary
    log_message("=== STEP 5 COMPLETED SUCCESSFULLY ===")
    log_message(f"✅ Query processed successfully")
    log_message(f"✅ Found {len(results)} similar documents")
    log_message(f"✅ Search time: {search_time:.4f} seconds")
    log_message(f"✅ Total time: {total_time:.4f} seconds")
    
    if timing_mode:
        print(f"\n⏱️  PERFORMANCE METRICS:")
        print(f"   Search time: {search_time:.4f}s")
        print(f"   Total time: {total_time:.4f}s")
        print(f"   Target: < 5.0s {'✅ PASS' if total_time < 5.0 else '❌ FAIL'}")

if __name__ == "__main__":
    main() 