#!/usr/bin/env python3.8
"""
Debug model name extraction from Ollama response
"""

import sys

def debug_model_extraction():
    """Debug model name extraction"""
    print("🔍 Debugging model name extraction...")
    
    try:
        import ollama
        
        client = ollama.Client(host='http://localhost:11434')
        models = client.list()
        
        print(f"Raw models response: {models}")
        print(f"Type: {type(models)}")
        
        # Check response format
        if hasattr(models, 'models'):
            model_list = models.models
            print(f"✅ Found models.models: {len(model_list)} items")
        else:
            print("❌ No models.models attribute")
            return False
        
        # Debug each model
        for i, m in enumerate(model_list):
            print(f"\n--- Model {i+1} ---")
            print(f"Type: {type(m)}")
            print(f"Raw: {m}")
            
            # Check attributes
            if hasattr(m, 'model'):
                print(f"✅ m.model = '{m.model}'")
            if hasattr(m, 'name'):
                print(f"✅ m.name = '{m.name}'")
            
            # Check dict access
            if isinstance(m, dict):
                print(f"✅ Dict keys: {list(m.keys())}")
                if 'model' in m:
                    print(f"✅ m['model'] = '{m['model']}'")
                if 'name' in m:
                    print(f"✅ m['name'] = '{m['name']}'")
            
            # Try string extraction
            model_str = str(m)
            print(f"String representation: {model_str}")
            
            if "model='" in model_str:
                start = model_str.find("model='") + 7
                end = model_str.find("'", start)
                if end > start:
                    extracted = model_str[start:end]
                    print(f"✅ Extracted from string: '{extracted}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

if __name__ == "__main__":
    success = debug_model_extraction()
    sys.exit(0 if success else 1) 