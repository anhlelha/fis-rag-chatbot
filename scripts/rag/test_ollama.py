#!/usr/bin/env python3.8
"""
US-004 Step 1: Test Ollama Integration
Test connection to Ollama server and Mistral 7B model functionality
"""

import sys
import time
import json
from datetime import datetime

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_ollama_import():
    """Test if Ollama library can be imported"""
    log_message("Testing Ollama library import...")
    
    try:
        import ollama
        log_message("✅ Ollama library imported successfully")
        return True
    except ImportError as e:
        log_message(f"❌ Failed to import Ollama library: {str(e)}", "ERROR")
        log_message("Run: pip3.8 install ollama", "ERROR")
        return False

def test_ollama_connection():
    """Test connection to Ollama server"""
    log_message("Testing Ollama server connection...")
    
    try:
        import ollama
        
        # Create client with default host
        client = ollama.Client(host='http://localhost:11434')
        log_message("✅ Ollama client created successfully")
        
        # Test connection by listing models
        models = client.list()
        log_message(f"✅ Connected to Ollama server")
        log_message(f"   Available models: {len(models.get('models', []))}")
        
        return True, client
    except Exception as e:
        log_message(f"❌ Failed to connect to Ollama server: {str(e)}", "ERROR")
        log_message("Make sure Ollama is running on localhost:11434", "ERROR")
        return False, None

def test_mistral_model(client):
    """Test Mistral 7B model availability and response"""
    log_message("Testing Mistral 7B model...")
    
    try:
        # Check if Mistral model is available
        models = client.list()
        mistral_available = any('mistral' in model.get('name', '').lower() 
                              for model in models.get('models', []))
        
        if not mistral_available:
            log_message("❌ Mistral model not found", "ERROR")
            log_message("Run: ollama pull mistral", "ERROR")
            return False
        
        log_message("✅ Mistral model found")
        
        # Test English query
        log_message("Testing English query...")
        english_query = "Hello, how are you? Please respond briefly."
        
        start_time = time.time()
        response = client.chat(model='mistral', messages=[
            {'role': 'user', 'content': english_query}
        ])
        english_time = time.time() - start_time
        
        english_response = response['message']['content']
        log_message(f"✅ English response received in {english_time:.2f}s")
        log_message(f"   Response: {english_response[:100]}...")
        
        # Test Vietnamese query
        log_message("Testing Vietnamese query...")
        vietnamese_query = "Xin chào, bạn khỏe không? Hãy trả lời ngắn gọn."
        
        start_time = time.time()
        response = client.chat(model='mistral', messages=[
            {'role': 'user', 'content': vietnamese_query}
        ])
        vietnamese_time = time.time() - start_time
        
        vietnamese_response = response['message']['content']
        log_message(f"✅ Vietnamese response received in {vietnamese_time:.2f}s")
        log_message(f"   Response: {vietnamese_response[:100]}...")
        
        # Performance check
        avg_time = (english_time + vietnamese_time) / 2
        log_message(f"✅ Average response time: {avg_time:.2f}s")
        
        if avg_time > 30:
            log_message("⚠️  Response time > 30s - may be slow for RAG", "WARNING")
        else:
            log_message("✅ Response time acceptable for RAG pipeline")
        
        return True
        
    except Exception as e:
        log_message(f"❌ Mistral model test failed: {str(e)}", "ERROR")
        return False

def test_model_info(client):
    """Get detailed model information"""
    log_message("Getting model information...")
    
    try:
        models = client.list()
        
        for model in models.get('models', []):
            if 'mistral' in model.get('name', '').lower():
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                modified = model.get('modified_at', 'Unknown')
                
                # Convert size to human readable
                size_gb = size / (1024**3) if size else 0
                
                log_message(f"✅ Model Details:")
                log_message(f"   Name: {name}")
                log_message(f"   Size: {size_gb:.1f} GB")
                log_message(f"   Modified: {modified}")
                break
        
        return True
    except Exception as e:
        log_message(f"❌ Failed to get model info: {str(e)}", "ERROR")
        return False

def generate_test_report(results):
    """Generate test report"""
    log_message("=== US-004 STEP 1 TEST REPORT ===")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    log_message(f"Tests Passed: {passed_tests}/{total_tests}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log_message(f"- {test_name}: {status}")
    
    overall_status = "PASS" if passed_tests == total_tests else "FAIL"
    log_message(f"Overall Status: {overall_status}")
    
    if overall_status == "PASS":
        log_message("🎉 US-004 Step 1 completed successfully!")
        log_message("Ready to proceed to Step 2: Query Processing Pipeline")
    else:
        log_message("❌ US-004 Step 1 failed - Please fix errors above")
    
    return overall_status == "PASS"

def main():
    """Main test function"""
    log_message("=== US-004 STEP 1: OLLAMA INTEGRATION SETUP TEST ===")
    log_message("Testing Ollama connection and Mistral 7B model...")
    
    results = {}
    
    # Test 1: Import Ollama library
    results['Ollama Library Import'] = test_ollama_import()
    if not results['Ollama Library Import']:
        generate_test_report(results)
        sys.exit(1)
    
    # Test 2: Connect to Ollama server
    connection_success, client = test_ollama_connection()
    results['Ollama Server Connection'] = connection_success
    if not connection_success:
        generate_test_report(results)
        sys.exit(1)
    
    # Test 3: Test Mistral model
    results['Mistral Model Test'] = test_mistral_model(client)
    
    # Test 4: Get model information
    results['Model Information'] = test_model_info(client)
    
    # Generate final report
    success = generate_test_report(results)
    
    if success:
        # Save success status for checklist update
        with open('/tmp/us004_step1_status.txt', 'w') as f:
            f.write('SUCCESS')
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 