#!/usr/bin/env python3.8
"""
Debug Ollama Connection
Check Ollama service and model availability
"""

import sys
import json

def debug_ollama():
    """Debug Ollama connection"""
    print("🔍 Debugging Ollama connection...")
    
    # Check if ollama module is available
    try:
        import ollama
        print("✅ ollama module imported successfully")
    except ImportError as e:
        print(f"❌ Cannot import ollama: {e}")
        print("Install with: pip3.8 install ollama")
        return False
    
    # Test connection
    try:
        client = ollama.Client(host='http://localhost:11434')
        print("✅ Ollama client created")
        
        # Test list models
        print("\n📋 Testing model list...")
        models = client.list()
        print(f"Raw response: {models}")
        
        if not models:
            print("❌ Empty response from Ollama")
            return False
        
        if 'models' not in models:
            print("❌ 'models' key not found in response")
            print("Response keys:", list(models.keys()) if isinstance(models, dict) else "Not a dict")
            return False
        
        model_list = models['models']
        print(f"✅ Found {len(model_list)} models")
        
        if not model_list:
            print("❌ No models available")
            print("Pull a model with: ollama pull mistral:7b")
            return False
        
        print("\n📚 Available models:")
        for i, model in enumerate(model_list):
            print(f"  {i+1}. {model}")
            if isinstance(model, dict):
                name = model.get('name', 'unknown')
                size = model.get('size', 'unknown')
                print(f"     Name: {name}")
                print(f"     Size: {size}")
        
        # Check for mistral model
        print(f"\n🔍 Checking for mistral:7b model...")
        mistral_found = False
        for model in model_list:
            model_name = model.get('name', '') if isinstance(model, dict) else str(model)
            if 'mistral' in model_name.lower():
                print(f"✅ Found Mistral model: {model_name}")
                mistral_found = True
        
        if not mistral_found:
            print("❌ Mistral model not found")
            print("Pull with: ollama pull mistral:7b")
            return False
        
        # Test simple generation
        print(f"\n🧪 Testing simple generation...")
        try:
            response = client.generate(
                model='mistral:7b',
                prompt='Hello, how are you?',
                options={'num_predict': 10}
            )
            print("✅ Generation test successful")
            print(f"Response: {response.get('response', 'No response')[:100]}...")
            
        except Exception as e:
            print(f"❌ Generation test failed: {e}")
            return False
        
        print("\n✅ All Ollama checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if Ollama service is running: systemctl status ollama")
        print("2. Check if port 11434 is open: netstat -tlnp | grep 11434")
        print("3. Try manual connection: curl http://localhost:11434/api/tags")
        return False

if __name__ == "__main__":
    success = debug_ollama()
    sys.exit(0 if success else 1) 