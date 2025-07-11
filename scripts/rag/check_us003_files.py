#!/usr/bin/env python3.8
"""
Check US-003 Vector Database Files
Verify structure and content from US-003 completion
"""

import os
import sys
import json

def check_us003_files():
    """Check US-003 vector database files"""
    print("🔍 Checking US-003 vector database files...")
    
    # US-003 file paths from checklist
    us003_files = {
        "vector_db": "/opt/rag-copilot/db/vector_db.index",
        "metadata": "/opt/rag-copilot/db/vector_db_metadata.json",
        "chunks_backup": "/opt/rag-copilot/db/chunks_backup.pkl",
        "embeddings_backup": "/opt/rag-copilot/db/embeddings_backup.npy"
    }
    
    print("\n📂 Checking US-003 files:")
    found_files = []
    
    for name, path in us003_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name}: {path} - {size} bytes")
            found_files.append((name, path))
        else:
            print(f"❌ {name}: {path} - NOT FOUND")
    
    if not found_files:
        print("\n❌ No US-003 files found!")
        print("🔧 Solution: Complete US-003 first or check file locations")
        return False
    
    # Check metadata structure
    metadata_path = "/opt/rag-copilot/db/vector_db_metadata.json"
    if os.path.exists(metadata_path):
        print(f"\n📋 Checking metadata structure...")
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            print(f"✅ Metadata loaded successfully")
            print(f"📊 Metadata keys: {list(metadata.keys())}")
            
            # Check if it has document data
            if 'chunks' in metadata:
                chunks = metadata['chunks']
                print(f"📄 Found {len(chunks)} chunks")
                
                # Show first chunk structure
                if chunks:
                    first_chunk = chunks[0]
                    print(f"📝 First chunk keys: {list(first_chunk.keys())}")
                    if 'content' in first_chunk:
                        content_preview = first_chunk['content'][:100]
                        print(f"📖 Content preview: {content_preview}...")
            
            elif isinstance(metadata, dict) and any(str(i) in metadata for i in range(10)):
                # Check if it's indexed by numbers
                print(f"📄 Found indexed metadata")
                indices = [k for k in metadata.keys() if k.isdigit()]
                print(f"📊 Document indices: {indices}")
                
                if indices:
                    first_doc = metadata[indices[0]]
                    print(f"📝 First document keys: {list(first_doc.keys())}")
                    if 'content' in first_doc:
                        content_preview = first_doc['content'][:100]
                        print(f"📖 Content preview: {content_preview}...")
            
            else:
                print("⚠️  Unknown metadata structure")
                print(f"📋 Metadata sample: {str(metadata)[:200]}...")
                
        except Exception as e:
            print(f"❌ Failed to read metadata: {e}")
            return False
    
    # Check FAISS index
    vector_db_path = "/opt/rag-copilot/db/vector_db.index"
    if os.path.exists(vector_db_path):
        print(f"\n🗂️  Checking FAISS index...")
        try:
            import faiss
            index = faiss.read_index(vector_db_path)
            print(f"✅ FAISS index loaded successfully")
            print(f"📊 Total vectors: {index.ntotal}")
            print(f"📏 Vector dimension: {index.d}")
            
        except ImportError:
            print("⚠️  FAISS not available, cannot check index")
        except Exception as e:
            print(f"❌ Failed to read FAISS index: {e}")
            return False
    
    print(f"\n💡 Integration recommendations:")
    print("✅ US-003 files found and accessible")
    print("✅ Update Step 4 to use correct file paths")
    print("✅ Verify metadata format compatibility")
    
    return True

if __name__ == "__main__":
    success = check_us003_files()
    sys.exit(0 if success else 1) 