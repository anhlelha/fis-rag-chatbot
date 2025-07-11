#!/usr/bin/env python3.8
"""
US-003 Step 3: Generate embeddings for document chunks
Process embedding_ready.json from US-002 and create vector embeddings
"""

import json
import numpy as np
import pickle
import os
import sys
from datetime import datetime
from sentence_transformers import SentenceTransformer

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def load_embedding_ready_data(file_path):
    """Load the embedding_ready.json file from US-002"""
    log_message(f"Loading embedding data from: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        log_message(f"✅ Data loaded successfully")
        log_message(f"   - Total chunks: {len(data.get('chunks', []))}")
        log_message(f"   - Source file: {data.get('source_file', 'Unknown')}")
        
        return data
    except Exception as e:
        log_message(f"❌ Failed to load data: {str(e)}", "ERROR")
        return None

def initialize_embedding_model():
    """Initialize the sentence transformer model"""
    log_message("Initializing embedding model...")
    
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        log_message("✅ Model loaded successfully")
        log_message(f"   - Model: all-MiniLM-L6-v2")
        log_message(f"   - Embedding dimension: {model.get_sentence_embedding_dimension()}")
        
        return model
    except Exception as e:
        log_message(f"❌ Failed to load model: {str(e)}", "ERROR")
        return None

def generate_embeddings(model, chunks):
    """Generate embeddings for all chunks"""
    log_message(f"Generating embeddings for {len(chunks)} chunks...")
    
    try:
        # Extract text content from chunks
        texts = []
        for i, chunk in enumerate(chunks):
            # Handle both dict (chunks) and string (documents) formats
            if isinstance(chunk, dict):
                text = chunk.get('content', chunk.get('text', ''))
            else:
                text = str(chunk)
            
            if not text:
                log_message(f"⚠️  Chunk {i} has no content", "WARNING")
                text = ""
            texts.append(text)
        
        log_message(f"   - Processing {len(texts)} text chunks")
        
        # Generate embeddings
        embeddings = model.encode(texts, show_progress_bar=True)
        
        log_message(f"✅ Embeddings generated successfully")
        log_message(f"   - Shape: {embeddings.shape}")
        log_message(f"   - Dimension: {embeddings.shape[1]}")
        log_message(f"   - Data type: {embeddings.dtype}")
        
        return embeddings
    except Exception as e:
        log_message(f"❌ Failed to generate embeddings: {str(e)}", "ERROR")
        return None

def save_embeddings(embeddings, chunks, output_dir, source_file):
    """Save embeddings in multiple formats"""
    log_message(f"Saving embeddings to: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 1. Save raw embeddings as numpy array
        embeddings_file = os.path.join(output_dir, "embeddings.npy")
        np.save(embeddings_file, embeddings)
        log_message(f"✅ Raw embeddings saved: {embeddings_file}")
        
        # 2. Save embeddings with metadata as pickle
        embeddings_with_metadata = {
            'embeddings': embeddings,
            'chunks': chunks,
            'source_file': source_file,
            'model': 'all-MiniLM-L6-v2',
            'embedding_dimension': embeddings.shape[1],
            'total_chunks': len(chunks),
            'created_at': datetime.now().isoformat()
        }
        
        pickle_file = os.path.join(output_dir, "embeddings_with_metadata.pkl")
        with open(pickle_file, 'wb') as f:
            pickle.dump(embeddings_with_metadata, f)
        log_message(f"✅ Embeddings with metadata saved: {pickle_file}")
        
        # 3. Save summary JSON
        summary = {
            'source_file': source_file,
            'total_chunks': len(chunks),
            'embedding_dimension': int(embeddings.shape[1]),
            'model_name': 'all-MiniLM-L6-v2',
            'files_created': {
                'raw_embeddings': embeddings_file,
                'embeddings_with_metadata': pickle_file
            },
            'embedding_stats': {
                'mean': float(np.mean(embeddings)),
                'std': float(np.std(embeddings)),
                'min': float(np.min(embeddings)),
                'max': float(np.max(embeddings))
            },
            'created_at': datetime.now().isoformat()
        }
        
        summary_file = os.path.join(output_dir, "embedding_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        log_message(f"✅ Summary saved: {summary_file}")
        
        return True
    except Exception as e:
        log_message(f"❌ Failed to save embeddings: {str(e)}", "ERROR")
        return False

def main():
    """Main embedding generation process"""
    log_message("=== US-003 STEP 3: GENERATE EMBEDDINGS ===")
    
    # Check command line arguments
    if len(sys.argv) != 2:
        log_message("Usage: python3.8 embed_chunks.py <embedding_ready.json>", "ERROR")
        log_message("Example: python3.8 embed_chunks.py /opt/rag-copilot/output/AI-Starter-Kit_final_output/embedding_ready.json", "ERROR")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Validate input file
    if not os.path.exists(input_file):
        log_message(f"❌ Input file not found: {input_file}", "ERROR")
        sys.exit(1)
    
    # Create output directory
    output_dir = "/opt/rag-copilot/output/embeddings"
    
    # Step 1: Load data
    data = load_embedding_ready_data(input_file)
    if not data:
        log_message("❌ Failed to load input data", "ERROR")
        sys.exit(1)
    
    # Try both 'chunks' and 'documents' keys for compatibility
    chunks = data.get('chunks', [])
    if not chunks:
        chunks = data.get('documents', [])
    
    if not chunks:
        log_message("❌ No chunks/documents found in input data", "ERROR")
        log_message("Available keys: " + str(list(data.keys())), "ERROR")
        sys.exit(1)
    
    # Step 2: Initialize model
    model = initialize_embedding_model()
    if not model:
        log_message("❌ Failed to initialize model", "ERROR")
        sys.exit(1)
    
    # Step 3: Generate embeddings
    embeddings = generate_embeddings(model, chunks)
    if embeddings is None:
        log_message("❌ Failed to generate embeddings", "ERROR")
        sys.exit(1)
    
    # Step 4: Save embeddings
    success = save_embeddings(embeddings, chunks, output_dir, data.get('source_file', input_file))
    if not success:
        log_message("❌ Failed to save embeddings", "ERROR")
        sys.exit(1)
    
    # Success summary
    log_message("=== STEP 3 COMPLETED SUCCESSFULLY ===")
    log_message(f"✅ Generated embeddings for {len(chunks)} chunks")
    log_message(f"✅ Embedding dimension: {embeddings.shape[1]}")
    log_message(f"✅ Output directory: {output_dir}")
    log_message(f"✅ Files created:")
    log_message(f"   - embeddings.npy (raw embeddings)")
    log_message(f"   - embeddings_with_metadata.pkl (embeddings + metadata)")
    log_message(f"   - embedding_summary.json (summary)")
    log_message("")
    log_message("🚀 Ready for Step 4: Initialize vector database")

if __name__ == "__main__":
    main() 