#!/usr/bin/env python3.8
"""
Test Script for Step 4: RAG Response Generation
Simple validation script to test prompt engineering and LLM integration.

Usage:
    python3.8 test_step4.py
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_step4():
    """Test Step 4 RAG Response Generation"""
    
    print("🧪 Testing Step 4: RAG Response Generation")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "query": "Quy trình nghỉ phép của công ty như thế nào?",
            "language": "vietnamese",
            "description": "Vietnamese query about leave process"
        },
        {
            "query": "What is the expense reimbursement process?", 
            "language": "english",
            "description": "English query about expense reimbursement"
        },
        {
            "query": "Làm thế nào để xin tăng lương?",
            "language": "vietnamese", 
            "description": "Vietnamese query about salary increase"
        }
    ]
    
    try:
        # Try importing from current directory first
        import generate_response
        RAGResponseGenerator = generate_response.RAGResponseGenerator
        print("✅ RAG Response Generator imported successfully")
        
        # Initialize generator
        print("\n🔧 Initializing RAG Response Generator...")
        generator = RAGResponseGenerator()
        print("✅ Generator initialized successfully")
        
        # Run test cases
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {test_case['description']}")
            print(f"📝 Query: {test_case['query']}")
            
            try:
                # Generate response with shorter token limit for testing
                result = generator.generate_response(
                    test_case['query'], 
                    max_tokens=300,
                    temperature=0.3
                )
                
                if result['success']:
                    print(f"✅ Test {i} PASSED")
                    print(f"⏱️  Processing time: {result['timing']['total']:.3f}s")
                    print(f"📚 Context sources: {result['context_count']}")
                    print(f"🔤 Response length: {len(result['response'])} chars")
                    
                    # Check performance target
                    if result['timing']['total'] < 15:
                        print(f"🎯 Performance target MET: {result['timing']['total']:.3f}s < 15s")
                    else:
                        print(f"⚠️  Performance target MISSED: {result['timing']['total']:.3f}s > 15s")
                    
                    # Show first 200 chars of response
                    response_preview = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
                    print(f"📖 Response preview: {response_preview}")
                    
                else:
                    print(f"❌ Test {i} FAILED: {result.get('error', 'Unknown error')}")
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ Test {i} ERROR: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "query": test_case['query']
                })
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in results if r.get('success', False))
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 All tests PASSED! Step 4 is working correctly.")
            
            # Calculate average performance
            avg_time = sum(r['timing']['total'] for r in results if r.get('success', False)) / passed
            print(f"⚡ Average processing time: {avg_time:.3f}s")
            
            if avg_time < 15:
                print("🎯 Average performance meets Epic target (<15s)")
            else:
                print("⚠️  Average performance exceeds Epic target (>15s)")
                
        else:
            print("⚠️  Some tests failed. Check the errors above.")
        
        # Save test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"step4_test_results_{timestamp}.json"
        
        test_summary = {
            "timestamp": datetime.now().isoformat(),
            "step": "Step 4: RAG Response Generation",
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "average_time": avg_time if passed > 0 else 0,
            "results": results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_summary, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Test results saved to: {results_file}")
        
        return passed == total
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure generate_response.py is in the same directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Step 4 Test Suite")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_step4()
    
    if success:
        print("\n✅ Step 4 validation completed successfully!")
        print("🎯 Ready to proceed to Step 5: End-to-End RAG Pipeline")
        return 0
    else:
        print("\n❌ Step 4 validation failed!")
        print("🔧 Please check the errors and fix issues before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 