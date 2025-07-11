#!/usr/bin/env python3.8
"""
Fast RAG Response Generation - Optimized for Speed
Reduced context size to avoid LLM timeout issues
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_fast_rag():
    """Test RAG with optimized settings"""
    print("🚀 Fast RAG Response Generation Test")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        from generate_response import RAGResponseGenerator
        
        # Initialize with optimized settings
        generator = RAGResponseGenerator()
        
        # Test queries with fast settings
        test_queries = [
            "AI tools",
            "ChatGPT",
            "NotebookLM"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test {i}: {query}")
            
            try:
                result = generator.generate_response(
                    query,
                    max_tokens=100,      # Reduced from 300
                    temperature=0.1      # Lower temperature for faster generation
                )
                
                if result.get('success', False):
                    timing = result.get('timing', {})
                    print(f"✅ SUCCESS in {timing.get('total', 0):.3f}s")
                    print(f"   Context: {timing.get('context_retrieval', 0):.3f}s")
                    print(f"   LLM: {timing.get('llm_generation', 0):.3f}s")
                    print(f"   Response: {result['response'][:100]}...")
                    
                    # Check performance target
                    if timing.get('total', 0) < 15:
                        print(f"🎯 Performance target MET: {timing.get('total', 0):.3f}s < 15s")
                    else:
                        print(f"⚠️  Performance target MISSED: {timing.get('total', 0):.3f}s > 15s")
                else:
                    print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
        
        print(f"\n✅ Fast RAG test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Fast RAG test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_fast_rag()
    sys.exit(0 if success else 1) 