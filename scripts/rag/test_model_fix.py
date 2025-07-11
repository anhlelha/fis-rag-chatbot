#!/usr/bin/env python3.8
"""
Test model extraction fix directly
"""

import sys
import os

def test_model_extraction_fix():
    """Test the model extraction fix"""
    print("🧪 Testing model extraction fix...")
    
    try:
        import ollama
        
        # Test the exact same logic as in generate_response.py
        client = ollama.Client(host='http://localhost:11434')
        models = client.list()
        print(f"✅ Ollama client connected")
        
        # Handle different response formats (same as generate_response.py)
        model_list = []
        if hasattr(models, 'models'):
            # New format: models.models (list of Model objects)
            model_list = models.models
            print(f"✅ Found {len(model_list)} models (new format)")
        elif isinstance(models, dict) and 'models' in models:
            # Old format: models['models'] (dictionary)
            model_list = models['models']
            print(f"✅ Found {len(model_list)} models (dict format)")
        else:
            print("❌ Invalid response from Ollama server")
            return False
        
        # Extract model names (same logic as generate_response.py)
        model_names = []
        for m in model_list:
            model_name = None
            
            print(f"\n🔍 Processing model: {type(m)}")
            
            if hasattr(m, 'model'):
                # Model object with .model attribute
                model_name = m.model
                print(f"✅ Found m.model = '{model_name}'")
            elif hasattr(m, 'name'):
                # Model object with .name attribute
                model_name = m.name
                print(f"✅ Found m.name = '{model_name}'")
            elif isinstance(m, dict) and 'name' in m:
                # Dictionary with 'name' key
                model_name = m['name']
                print(f"✅ Found m['name'] = '{model_name}'")
            elif isinstance(m, dict) and 'model' in m:
                # Dictionary with 'model' key
                model_name = m['model']
                print(f"✅ Found m['model'] = '{model_name}'")
            else:
                # Try to extract from string representation
                model_str = str(m)
                print(f"⚠️  Fallback to string extraction: {model_str[:100]}...")
                if "model='" in model_str:
                    # Extract from "model='mistral:7b'"
                    start = model_str.find("model='") + 7
                    end = model_str.find("'", start)
                    if end > start:
                        model_name = model_str[start:end]
                        print(f"✅ Extracted from string: '{model_name}'")
                else:
                    model_name = model_str
                    print(f"⚠️  Using full string: '{model_name}'")
            
            if model_name:
                model_names.append(model_name)
                print(f"✅ Added to list: '{model_name}'")
            else:
                model_names.append('unknown')
                print(f"❌ Added 'unknown' to list")
        
        print(f"\n📋 Final model list: {model_names}")
        
        # Test model search
        target_model = "mistral:7b"
        model_found = any(target_model in name for name in model_names)
        
        print(f"\n🔍 Looking for '{target_model}'...")
        print(f"Result: {model_found}")
        
        if model_found:
            print("✅ Model extraction fix is working correctly!")
            return True
        else:
            print("❌ Model extraction fix failed!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_model_extraction_fix()
    sys.exit(0 if success else 1) 