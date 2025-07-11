#!/usr/bin/env python3.8
"""
US-003 Step 4: Initialize and save vector database
Create FAISS vector database from embeddings generated in Step 3
"""

import pickle
import numpy as np
import faiss
import json
import os
import sys
from datetime import datetime

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def load_embeddings(embeddings_dir):
    """Load embeddings and metadata from Step 3 output"""
    log_message(f"Loading embeddings from: {embeddings_dir}")
    
    try:
        # Load embeddings with metadata
        metadata_file = os.path.join(embeddings_dir, "embeddings_with_metadata.pkl")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'rb') as f:
                data = pickle.load(f)
            
            embeddings = data['embeddings']
            chunks = data['chunks']
            log_message(f"✅ Embeddings with metadata loaded")
        else:
            # Fallback to raw embeddings
            embeddings_file = os.path.join(embeddings_dir, "embeddings.npy")
            embeddings = np.load(embeddings_file)
            chunks = None
            log_message(f"✅ Raw embeddings loaded (no metadata)")
        
        log_message(f"   - Embeddings shape: {embeddings.shape}")
        log_message(f"   - Embedding dimension: {embeddings.shape[1]}")
        log_message(f"   - Total vectors: {embeddings.shape[0]}")
        
        return embeddings, chunks
    except Exception as e:
        log_message(f"❌ Failed to load embeddings: {str(e)}", "ERROR")
        return None, None

def create_faiss_index(embeddings, index_type="IndexFlatL2"):
    """Create FAISS index from embeddings"""
    log_message(f"Creating FAISS index: {index_type}")
    
    try:
        dimension = embeddings.shape[1]
        
        # Create index based on type
        if index_type == "IndexFlatL2":
            index = faiss.IndexFlatL2(dimension)
            log_message("   - Using exact L2 distance search")
        elif index_type == "IndexFlatIP":
            index = faiss.IndexFlatIP(dimension)
            log_message("   - Using exact inner product search")
        elif index_type == "IndexIVFFlat":
            # For larger datasets, use IVF (Inverted File) for faster search
            n_clusters = min(100, embeddings.shape[0] // 10)
            quantizer = faiss.IndexFlatL2(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, n_clusters)
            log_message(f"   - Using IVF with {n_clusters} clusters")
        else:
            # Default to exact search
            index = faiss.IndexFlatL2(dimension)
            log_message("   - Using default IndexFlatL2")
        
        # Ensure embeddings are float32
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
            log_message("   - Converted embeddings to float32")
        
        # Train index if needed (for IVF)
        if index_type == "IndexIVFFlat":
            log_message("   - Training IVF index...")
            index.train(embeddings)
        
        # Add vectors to index
        log_message("   - Adding vectors to index...")
        index.add(embeddings)
        
        log_message(f"✅ FAISS index created successfully")
        log_message(f"   - Index type: {index_type}")
        log_message(f"   - Total vectors: {index.ntotal}")
        log_message(f"   - Is trained: {index.is_trained}")
        
        return index
    except Exception as e:
        log_message(f"❌ Failed to create FAISS index: {str(e)}", "ERROR")
        return None

def test_index_search(index, embeddings, k=3):
    """Test the index with a sample search"""
    log_message("Testing index search functionality...")
    
    try:
        # Use first embedding as query
        query = embeddings[0:1].astype(np.float32)
        
        # Search
        distances, indices = index.search(query, k)
        
        log_message(f"✅ Search test successful")
        log_message(f"   - Query shape: {query.shape}")
        log_message(f"   - Top {k} results: {indices[0]}")
        log_message(f"   - Distances: {distances[0]}")
        
        return True
    except Exception as e:
        log_message(f"❌ Search test failed: {str(e)}", "ERROR")
        return False

def save_vector_database(index, embeddings, chunks, output_dir):
    """Save FAISS index and related data"""
    log_message(f"Saving vector database to: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 1. Save FAISS index
        index_file = os.path.join(output_dir, "vector_db.index")
        faiss.write_index(index, index_file)
        log_message(f"✅ FAISS index saved: {index_file}")
        
        # 2. Save database metadata
        metadata = {
            'index_type': type(index).__name__,
            'total_vectors': int(index.ntotal),
            'dimension': int(embeddings.shape[1]),
            'is_trained': bool(index.is_trained),
            'created_at': datetime.now().isoformat(),
            'model_name': 'all-MiniLM-L6-v2',
            'files': {
                'index': index_file,
                'embeddings': os.path.join(output_dir, "embeddings_backup.npy"),
                'chunks': os.path.join(output_dir, "chunks_backup.pkl") if chunks else None
            }
        }
        
        metadata_file = os.path.join(output_dir, "vector_db_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        log_message(f"✅ Database metadata saved: {metadata_file}")
        
        # 3. Save backup of embeddings
        embeddings_backup = os.path.join(output_dir, "embeddings_backup.npy")
        np.save(embeddings_backup, embeddings)
        log_message(f"✅ Embeddings backup saved: {embeddings_backup}")
        
        # 4. Save chunks backup if available
        if chunks:
            chunks_backup = os.path.join(output_dir, "chunks_backup.pkl")
            with open(chunks_backup, 'wb') as f:
                pickle.dump(chunks, f)
            log_message(f"✅ Chunks backup saved: {chunks_backup}")
        
        return True
    except Exception as e:
        log_message(f"❌ Failed to save vector database: {str(e)}", "ERROR")
        return False

def test_database_loading(output_dir):
    """Test loading the saved database"""
    log_message("Testing database loading...")
    
    try:
        # Load index
        index_file = os.path.join(output_dir, "vector_db.index")
        index = faiss.read_index(index_file)
        
        # Load metadata
        metadata_file = os.path.join(output_dir, "vector_db_metadata.json")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        log_message(f"✅ Database loaded successfully")
        log_message(f"   - Index type: {metadata['index_type']}")
        log_message(f"   - Total vectors: {index.ntotal}")
        log_message(f"   - Dimension: {metadata['dimension']}")
        
        return True
    except Exception as e:
        log_message(f"❌ Database loading test failed: {str(e)}", "ERROR")
        return False

def main():
    """Main vector database initialization process"""
    log_message("=== US-003 STEP 4: INITIALIZE VECTOR DATABASE ===")
    
    # Check command line arguments
    if len(sys.argv) != 2:
        log_message("Usage: python3.8 init_vector_db.py <embeddings_dir>", "ERROR")
        log_message("Example: python3.8 init_vector_db.py /opt/rag-copilot/output/embeddings", "ERROR")
        sys.exit(1)
    
    embeddings_dir = sys.argv[1]
    
    # Validate input directory
    if not os.path.exists(embeddings_dir):
        log_message(f"❌ Embeddings directory not found: {embeddings_dir}", "ERROR")
        sys.exit(1)
    
    # Create output directory
    output_dir = "/opt/rag-copilot/db"
    
    # Step 1: Load embeddings
    embeddings, chunks = load_embeddings(embeddings_dir)
    if embeddings is None:
        log_message("❌ Failed to load embeddings", "ERROR")
        sys.exit(1)
    
    # Step 2: Create FAISS index
    # Use exact search for small datasets, IVF for larger ones
    index_type = "IndexFlatL2" if embeddings.shape[0] < 1000 else "IndexIVFFlat"
    index = create_faiss_index(embeddings, index_type)
    if index is None:
        log_message("❌ Failed to create FAISS index", "ERROR")
        sys.exit(1)
    
    # Step 3: Test index
    if not test_index_search(index, embeddings):
        log_message("❌ Index search test failed", "ERROR")
        sys.exit(1)
    
    # Step 4: Save database
    if not save_vector_database(index, embeddings, chunks, output_dir):
        log_message("❌ Failed to save vector database", "ERROR")
        sys.exit(1)
    
    # Step 5: Test loading
    if not test_database_loading(output_dir):
        log_message("❌ Database loading test failed", "ERROR")
        sys.exit(1)
    
    # Success summary
    log_message("=== STEP 4 COMPLETED SUCCESSFULLY ===")
    log_message(f"✅ Vector database created and saved")
    log_message(f"✅ Index type: {index_type}")
    log_message(f"✅ Total vectors: {index.ntotal}")
    log_message(f"✅ Dimension: {embeddings.shape[1]}")
    log_message(f"✅ Database location: {output_dir}")
    log_message(f"✅ Files created:")
    log_message(f"   - vector_db.index (FAISS index)")
    log_message(f"   - vector_db_metadata.json (metadata)")
    log_message(f"   - embeddings_backup.npy (embeddings backup)")
    if chunks:
        log_message(f"   - chunks_backup.pkl (chunks backup)")
    log_message("")
    log_message("🚀 Ready for Step 5: Query vector database")

if __name__ == "__main__":
    main() 