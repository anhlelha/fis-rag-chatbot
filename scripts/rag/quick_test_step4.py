#!/usr/bin/env python3.8
"""
Quick Test for Step 4: RAG Response Generation
Simple validation without complex imports.

Usage:
    python3.8 quick_test_step4.py
"""

import sys
import os
import subprocess
import json
from datetime import datetime

def run_command(cmd):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_step4_basic():
    """Basic test for Step 4"""
    print("🧪 Quick Test for Step 4: RAG Response Generation")
    print("=" * 60)
    
    # Test cases
    test_queries = [
        "Quy trình nghỉ phép của công ty như thế nào?",
        "What is the expense reimbursement process?",
        "Làm thế nào để xin tăng lương?"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {query[:50]}...")
        
        # Build command
        cmd = f'python3.8 generate_response.py "{query}" --max-tokens 300 --output test_output_{i}.json'
        
        print(f"🔧 Running: {cmd}")
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print(f"✅ Test {i} PASSED")
            
            # Try to read output file
            output_file = f"test_output_{i}.json"
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                
                if result_data.get('success', False):
                    timing = result_data.get('timing', {})
                    total_time = timing.get('total', 0)
                    
                    print(f"⏱️  Processing time: {total_time:.3f}s")
                    print(f"📚 Context sources: {result_data.get('context_count', 0)}")
                    print(f"🔤 Response length: {len(result_data.get('response', ''))}")
                    
                    # Check performance
                    if total_time < 15:
                        print(f"🎯 Performance target MET: {total_time:.3f}s < 15s")
                    else:
                        print(f"⚠️  Performance target MISSED: {total_time:.3f}s > 15s")
                    
                    # Show response preview
                    response = result_data.get('response', '')
                    preview = response[:150] + "..." if len(response) > 150 else response
                    print(f"📖 Response preview: {preview}")
                    
                    results.append({
                        "test": i,
                        "query": query,
                        "success": True,
                        "timing": total_time,
                        "context_count": result_data.get('context_count', 0),
                        "response_length": len(response)
                    })
                else:
                    print(f"❌ Test {i} FAILED: {result_data.get('error', 'Unknown error')}")
                    results.append({
                        "test": i,
                        "query": query,
                        "success": False,
                        "error": result_data.get('error', 'Unknown error')
                    })
                
                # Clean up output file
                os.remove(output_file)
                
            except Exception as e:
                print(f"❌ Failed to read output: {e}")
                results.append({
                    "test": i,
                    "query": query,
                    "success": False,
                    "error": f"Failed to read output: {e}"
                })
        else:
            print(f"❌ Test {i} FAILED")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            results.append({
                "test": i,
                "query": query,
                "success": False,
                "error": f"Command failed: {stderr}"
            })
    
    return results

def main():
    """Main function"""
    print("🚀 Quick Test Suite for Step 4")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if generate_response.py exists
    if not os.path.exists('generate_response.py'):
        print("❌ generate_response.py not found in current directory")
        print("Please make sure you're in the scripts/rag directory")
        return 1
    
    # Run tests
    results = test_step4_basic()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed > 0:
        # Calculate average performance
        successful_results = [r for r in results if r.get('success', False) and 'timing' in r]
        if successful_results:
            avg_time = sum(r['timing'] for r in successful_results) / len(successful_results)
            print(f"⚡ Average processing time: {avg_time:.3f}s")
            
            if avg_time < 15:
                print("🎯 Average performance meets Epic target (<15s)")
            else:
                print("⚠️  Average performance exceeds Epic target (>15s)")
    
    if passed == total:
        print("🎉 All tests PASSED! Step 4 is working correctly.")
        print("🎯 Ready to proceed to Step 5: End-to-End RAG Pipeline")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 