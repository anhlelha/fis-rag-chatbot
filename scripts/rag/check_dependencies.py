#!/usr/bin/env python3.8
"""
Check dependencies for Step 4: RAG Response Generation
"""

import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies for Step 4...")
    
    missing_deps = []
    
    # Check Ollama
    try:
        import ollama
        print("✅ ollama - OK")
    except ImportError:
        print("❌ ollama - MISSING")
        missing_deps.append("ollama")
    
    # Check sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers - OK")
    except ImportError:
        print("❌ sentence-transformers - MISSING")
        missing_deps.append("sentence-transformers")
    
    # Check FAISS
    try:
        import faiss
        print("✅ faiss - OK")
    except ImportError:
        print("❌ faiss - MISSING")
        missing_deps.append("faiss-cpu")
    
    # Check numpy
    try:
        import numpy
        print("✅ numpy - OK")
    except ImportError:
        print("❌ numpy - MISSING")
        missing_deps.append("numpy")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("To install:")
        print(f"pip3.8 install {' '.join(missing_deps)}")
        return False
    else:
        print("\n✅ All dependencies are installed!")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1) 