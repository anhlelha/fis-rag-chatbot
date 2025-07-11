#!/usr/bin/env python3.8
"""
Simple test for generate_response.py fix
"""

import sys
import os
from datetime import datetime

def test_generate_response():
    """Test the fixed generate_response.py"""
    print("🧪 Testing generate_response.py fix...")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import the fixed module
        from generate_response import RAGResponseGenerator
        print("✅ generate_response module imported successfully")
        
        # Initialize generator (this will test the Ollama connection fix)
        print("\n🔧 Testing Ollama connection fix...")
        generator = RAGResponseGenerator()
        print("✅ RAGResponseGenerator initialized successfully")
        
        # Test a simple query
        print("\n🧪 Testing simple query...")
        result = generator.generate_response(
            "Hello, what is your name?",
            max_tokens=50,
            temperature=0.3
        )
        
        if result.get('success', False):
            print("✅ Query test PASSED")
            print(f"⏱️  Processing time: {result['timing']['total']:.3f}s")
            print(f"📝 Response: {result['response'][:100]}...")
            return True
        else:
            print(f"❌ Query test FAILED: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_generate_response()
    if success:
        print("\n✅ Fix verified! generate_response.py is working correctly.")
        print("🎯 Ready to proceed with Step 4 testing.")
    else:
        print("\n❌ Fix verification failed!")
    sys.exit(0 if success else 1) 