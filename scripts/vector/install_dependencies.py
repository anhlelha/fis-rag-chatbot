#!/usr/bin/env python3.8
"""
US-003 Step 1: Install embedding & vector DB dependencies
Auto-install script for CentOS 8
"""

import subprocess
import sys
import os
from datetime import datetime

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def run_command(command, description):
    """Run shell command and return result"""
    log_message(f"Running: {description}")
    log_message(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log_message(f"✅ SUCCESS: {description}")
            if result.stdout:
                log_message(f"Output: {result.stdout.strip()}")
            return True, result.stdout
        else:
            log_message(f"❌ FAILED: {description}", "ERROR")
            if result.stderr:
                log_message(f"Error: {result.stderr.strip()}", "ERROR")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        log_message(f"⏰ TIMEOUT: {description}", "ERROR")
        return False, "Command timed out"
    except Exception as e:
        log_message(f"💥 EXCEPTION: {description} - {str(e)}", "ERROR")
        return False, str(e)

def test_import(module_name, description):
    """Test if a module can be imported"""
    log_message(f"Testing import: {description}")
    try:
        __import__(module_name)
        log_message(f"✅ IMPORT SUCCESS: {description}")
        return True
    except ImportError as e:
        log_message(f"❌ IMPORT FAILED: {description} - {str(e)}", "ERROR")
        return False

def test_functionality():
    """Test basic functionality of installed libraries"""
    log_message("=== FUNCTIONALITY TESTING ===")
    
    # Test sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        test_embedding = model.encode(["test sentence"])
        log_message(f"✅ sentence-transformers: Model loaded, embedding dimension {len(test_embedding[0])}")
        sentence_transformers_ok = True
    except Exception as e:
        log_message(f"❌ sentence-transformers test failed: {str(e)}", "ERROR")
        sentence_transformers_ok = False
    
    # Test FAISS
    try:
        import faiss
        import numpy as np
        
        # Create sample data
        dimension = 384
        n_vectors = 10
        vectors = np.random.random((n_vectors, dimension)).astype('float32')
        
        # Create FAISS index
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)
        
        # Test search
        query = np.random.random((1, dimension)).astype('float32')
        distances, indices = index.search(query, k=3)
        
        log_message(f"✅ FAISS: Index created and search working, found {len(indices[0])} results")
        faiss_ok = True
    except Exception as e:
        log_message(f"❌ FAISS test failed: {str(e)}", "ERROR")
        faiss_ok = False
    
    # Test ChromaDB
    try:
        import chromadb
        
        # Create in-memory client
        client = chromadb.Client()
        collection = client.create_collection("test_collection")
        
        # Add test documents
        collection.add(
            documents=["This is a test document", "Another test document"],
            ids=["doc1", "doc2"]
        )
        
        # Test query
        results = collection.query(
            query_texts=["test"],
            n_results=2
        )
        
        log_message(f"✅ ChromaDB: Collection created and query working, found {len(results['documents'][0])} results")
        chromadb_ok = True
    except Exception as e:
        log_message(f"❌ ChromaDB test failed: {str(e)}", "ERROR")
        chromadb_ok = False
    
    return sentence_transformers_ok, faiss_ok, chromadb_ok

def main():
    """Main installation and testing process"""
    log_message("=== US-003 STEP 1: VECTOR DB DEPENDENCIES INSTALLATION ===")
    log_message("Target: CentOS 8 with Python 3.8")
    
    # Check Python version
    python_version = sys.version
    log_message(f"Python version: {python_version}")
    
    if not python_version.startswith("3.8"):
        log_message("⚠️  WARNING: Expected Python 3.8, but got different version", "WARNING")
    
    # Installation packages
    packages = [
        "sentence-transformers",
        "faiss-cpu", 
        "chromadb",
        "numpy",
        "torch"
    ]
    
    log_message("=== PACKAGE INSTALLATION ===")
    
    # Install packages
    install_success = True
    for package in packages:
        success, output = run_command(
            f"pip3.8 install {package}",
            f"Installing {package}"
        )
        if not success:
            install_success = False
            log_message(f"Failed to install {package}", "ERROR")
    
    if not install_success:
        log_message("❌ INSTALLATION FAILED - Some packages could not be installed", "ERROR")
        return False
    
    log_message("=== IMPORT TESTING ===")
    
    # Test imports
    import_tests = [
        ("sentence_transformers", "sentence-transformers"),
        ("faiss", "FAISS"),
        ("chromadb", "ChromaDB"),
        ("numpy", "NumPy"),
        ("torch", "PyTorch")
    ]
    
    import_success = True
    for module, description in import_tests:
        if not test_import(module, description):
            import_success = False
    
    if not import_success:
        log_message("❌ IMPORT TESTING FAILED - Some modules could not be imported", "ERROR")
        return False
    
    log_message("=== FUNCTIONALITY TESTING ===")
    
    # Test functionality
    st_ok, faiss_ok, chromadb_ok = test_functionality()
    
    functionality_success = st_ok and faiss_ok and chromadb_ok
    
    # Final summary
    log_message("=== INSTALLATION SUMMARY ===")
    log_message(f"Package Installation: {'✅ PASS' if install_success else '❌ FAIL'}")
    log_message(f"Import Testing: {'✅ PASS' if import_success else '❌ FAIL'}")
    log_message(f"Functionality Testing: {'✅ PASS' if functionality_success else '❌ FAIL'}")
    log_message(f"- sentence-transformers: {'✅ PASS' if st_ok else '❌ FAIL'}")
    log_message(f"- FAISS: {'✅ PASS' if faiss_ok else '❌ FAIL'}")
    log_message(f"- ChromaDB: {'✅ PASS' if chromadb_ok else '❌ FAIL'}")
    
    overall_success = install_success and import_success and functionality_success
    
    if overall_success:
        log_message("🎉 US-003 STEP 1 COMPLETED SUCCESSFULLY!")
        log_message("Ready to proceed to Step 2: Configure embedding model")
    else:
        log_message("❌ US-003 STEP 1 FAILED - Please check errors above", "ERROR")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 