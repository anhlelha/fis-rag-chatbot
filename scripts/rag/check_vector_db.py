#!/usr/bin/env python3.8
"""
Check Vector Database Files
Verify US-003 vector database setup
"""

import os
import sys

def check_vector_db():
    """Check vector database files"""
    print("🔍 Checking vector database files...")
    
    # Expected paths
    expected_paths = [
        "/opt/rag-copilot/data/vector_db/document_vectors.faiss",
        "/opt/rag-copilot/data/vector_db/document_metadata.json",
        "/opt/rag-copilot/data/processed_documents.json"
    ]
    
    # Alternative paths to check
    alternative_paths = [
        "./data/vector_db/document_vectors.faiss",
        "./data/vector_db/document_metadata.json", 
        "./data/processed_documents.json",
        "../data/vector_db/document_vectors.faiss",
        "../data/vector_db/document_metadata.json",
        "../data/processed_documents.json"
    ]
    
    print("\n📂 Checking expected paths:")
    found_files = []
    
    for path in expected_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {path} - {size} bytes")
            found_files.append(path)
        else:
            print(f"❌ {path} - NOT FOUND")
    
    print(f"\n📂 Checking alternative paths:")
    for path in alternative_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {path} - {size} bytes")
            found_files.append(path)
    
    # Check current directory structure
    print(f"\n📁 Current directory structure:")
    for root, dirs, files in os.walk('.'):
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        # Only show relevant files
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if any(ext in file for ext in ['.faiss', '.json', '.md']):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    print(f"{subindent}{file} - {size} bytes")
                except:
                    print(f"{subindent}{file} - ERROR")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if not found_files:
        print("❌ No vector database files found!")
        print("🔧 Solutions:")
        print("1. Complete US-003 first: Create vector database")
        print("2. Check if files are in different location")
        print("3. Run US-003 vector database creation script")
        return False
    
    elif len(found_files) < len(expected_paths):
        print("⚠️  Some vector database files missing!")
        print("🔧 Solutions:")
        print("1. Complete missing files from US-003")
        print("2. Update file paths in retrieve_context.py")
        print("3. Copy files to expected location")
        
        # Show copy commands
        print(f"\n📋 Copy commands (if files exist elsewhere):")
        for alt_path in alternative_paths:
            if os.path.exists(alt_path):
                expected_path = None
                if 'document_vectors.faiss' in alt_path:
                    expected_path = "/opt/rag-copilot/data/vector_db/document_vectors.faiss"
                elif 'document_metadata.json' in alt_path:
                    expected_path = "/opt/rag-copilot/data/vector_db/document_metadata.json"
                elif 'processed_documents.json' in alt_path:
                    expected_path = "/opt/rag-copilot/data/processed_documents.json"
                
                if expected_path:
                    print(f"mkdir -p {os.path.dirname(expected_path)}")
                    print(f"cp {alt_path} {expected_path}")
        
        return False
    
    else:
        print("✅ All vector database files found!")
        return True

if __name__ == "__main__":
    success = check_vector_db()
    sys.exit(0 if success else 1) 