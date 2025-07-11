#!/usr/bin/env python3.8
"""
Step-by-step test to identify timeout bottleneck
"""

import sys
import time
from datetime import datetime

def test_step_by_step():
    """Test each step individually to find bottleneck"""
    print("🔍 Step-by-step timeout diagnosis...")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Test imports
    print("\n🧪 Step 1: Testing imports...")
    start_time = time.time()
    try:
        from generate_response import RAGResponseGenerator
        print(f"✅ Imports successful in {time.time() - start_time:.3f}s")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Step 2: Test Ollama connection
    print("\n🧪 Step 2: Testing Ollama connection...")
    start_time = time.time()
    try:
        import ollama
        client = ollama.Client(host='http://localhost:11434')
        models = client.list()
        print(f"✅ Ollama connection successful in {time.time() - start_time:.3f}s")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False
    
    # Step 3: Test vector DB setup
    print("\n🧪 Step 3: Testing vector database setup...")
    start_time = time.time()
    try:
        from retrieve_context import setup_vector_db
        vector_db, model = setup_vector_db()
        print(f"✅ Vector DB setup successful in {time.time() - start_time:.3f}s")
    except Exception as e:
        print(f"❌ Vector DB setup failed: {e}")
        return False
    
    # Step 4: Test RAG generator initialization
    print("\n🧪 Step 4: Testing RAG generator initialization...")
    start_time = time.time()
    try:
        generator = RAGResponseGenerator()
        print(f"✅ RAG generator initialized in {time.time() - start_time:.3f}s")
    except Exception as e:
        print(f"❌ RAG generator initialization failed: {e}")
        return False
    
    # Step 5: Test context retrieval only
    print("\n🧪 Step 5: Testing context retrieval...")
    start_time = time.time()
    try:
        from retrieve_context import retrieve_context
        query = "Hello test"
        contexts = retrieve_context(query, vector_db, model, top_k=2, max_tokens=500)
        print(f"✅ Context retrieval successful in {time.time() - start_time:.3f}s")
        print(f"📄 Retrieved {len(contexts)} contexts")
    except Exception as e:
        print(f"❌ Context retrieval failed: {e}")
        return False
    
    # Step 6: Test LLM generation only
    print("\n🧪 Step 6: Testing LLM generation...")
    start_time = time.time()
    try:
        response = client.generate(
            model='mistral:7b',
            prompt='Hello, please respond briefly.',
            options={'num_predict': 50}
        )
        print(f"✅ LLM generation successful in {time.time() - start_time:.3f}s")
        print(f"📝 Response: {response['response'][:50]}...")
    except Exception as e:
        print(f"❌ LLM generation failed: {e}")
        return False
    
    # Step 7: Test full pipeline with minimal settings
    print("\n🧪 Step 7: Testing full pipeline (minimal)...")
    start_time = time.time()
    try:
        result = generator.generate_response(
            "Hello",
            max_tokens=50,  # Very small
            temperature=0.3
        )
        print(f"✅ Full pipeline successful in {time.time() - start_time:.3f}s")
        
        if result.get('success', False):
            print(f"📊 Timing breakdown:")
            timing = result.get('timing', {})
            print(f"  - Context retrieval: {timing.get('context_retrieval', 0):.3f}s")
            print(f"  - LLM generation: {timing.get('llm_generation', 0):.3f}s")
            print(f"  - Total: {timing.get('total', 0):.3f}s")
        else:
            print(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Full pipeline failed: {e}")
        return False
    
    print(f"\n✅ All steps completed successfully!")
    return True

if __name__ == "__main__":
    success = test_step_by_step()
    if success:
        print("\n🎯 No timeout issues found in step-by-step test")
        print("💡 Issue may be with specific queries or larger token limits")
    else:
        print("\n❌ Found bottleneck in step-by-step test")
    
    sys.exit(0 if success else 1) 