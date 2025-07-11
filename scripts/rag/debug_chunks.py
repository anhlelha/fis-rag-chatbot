#!/usr/bin/env python3.8
"""
Debug US-003 Chunks Structure
Examine the exact format of chunks_backup.pkl
"""

import os
import sys
import pickle
import json

def debug_chunks():
    """Debug chunks structure from US-003"""
    print("🔍 Debugging US-003 chunks structure...")
    
    chunks_path = "/opt/rag-copilot/db/chunks_backup.pkl"
    
    if not os.path.exists(chunks_path):
        print(f"❌ Chunks file not found: {chunks_path}")
        return False
    
    try:
        print(f"📂 Loading chunks from: {chunks_path}")
        with open(chunks_path, 'rb') as f:
            chunks = pickle.load(f)
        
        print(f"✅ Chunks loaded successfully")
        print(f"📊 Type: {type(chunks)}")
        print(f"📏 Length: {len(chunks)}")
        
        # Examine structure
        if isinstance(chunks, list):
            print(f"📋 Chunks is a list with {len(chunks)} items")
            
            for i, chunk in enumerate(chunks):
                print(f"\n--- Chunk {i} ---")
                print(f"Type: {type(chunk)}")
                
                if isinstance(chunk, dict):
                    print(f"Keys: {list(chunk.keys())}")
                    for key, value in chunk.items():
                        if isinstance(value, str):
                            preview = value[:100] + "..." if len(value) > 100 else value
                            print(f"  {key}: {preview}")
                        else:
                            print(f"  {key}: {type(value)} - {value}")
                
                elif isinstance(chunk, str):
                    preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                    print(f"Content: {preview}")
                
                else:
                    print(f"Raw: {chunk}")
                
                if i >= 2:  # Only show first 3 chunks
                    print("... (showing first 3 chunks only)")
                    break
        
        elif isinstance(chunks, dict):
            print(f"📋 Chunks is a dict with keys: {list(chunks.keys())}")
            
            for key, value in chunks.items():
                print(f"\n--- Key: {key} ---")
                print(f"Type: {type(value)}")
                
                if isinstance(value, dict):
                    print(f"Keys: {list(value.keys())}")
                elif isinstance(value, str):
                    preview = value[:100] + "..." if len(value) > 100 else value
                    print(f"Content: {preview}")
                else:
                    print(f"Raw: {value}")
        
        else:
            print(f"⚠️  Unexpected chunks type: {type(chunks)}")
            print(f"Raw: {chunks}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to debug chunks: {e}")
        return False

def debug_embeddings():
    """Debug embeddings structure"""
    print(f"\n🔍 Debugging embeddings structure...")
    
    embeddings_path = "/opt/rag-copilot/db/embeddings_backup.npy"
    
    if not os.path.exists(embeddings_path):
        print(f"❌ Embeddings file not found: {embeddings_path}")
        return False
    
    try:
        import numpy as np
        embeddings = np.load(embeddings_path)
        
        print(f"✅ Embeddings loaded successfully")
        print(f"📊 Shape: {embeddings.shape}")
        print(f"📏 Dtype: {embeddings.dtype}")
        print(f"📈 Sample values: {embeddings[0][:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to debug embeddings: {e}")
        return False

if __name__ == "__main__":
    chunks_ok = debug_chunks()
    embeddings_ok = debug_embeddings()
    
    if chunks_ok and embeddings_ok:
        print(f"\n💡 Integration recommendations:")
        print("✅ Update retrieve_context.py to handle actual chunk structure")
        print("✅ Match chunk format with Step 4 expectations")
    
    sys.exit(0 if chunks_ok else 1) 