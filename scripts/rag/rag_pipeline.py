#!/usr/bin/env python3.8
"""
US-004 Step 5: End-to-End RAG Pipeline Integration
Main orchestrator integrating all RAG components for complete pipeline.

Integration Flow:
US-002 (Document Processing) → US-003 (Vector Database) → 
Step 4 (RAG Response Generation) → Step 5 (End-to-End Pipeline)

Usage:
    python3.8 rag_pipeline.py "Quy trình nghỉ phép của công ty như thế nào?"
    python3.8 rag_pipeline.py "What is the expense reimbursement process?"
    python3.8 rag_pipeline.py "AI tools for developers"
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

class RAGPipeline:
    """
    End-to-End RAG Pipeline Orchestrator
    Integrates all components for complete RAG functionality
    """
    
    def __init__(self, config=None):
        """Initialize RAG Pipeline"""
        self.config = config or {
            "ollama_host": "http://localhost:11434",
            "model_name": "mistral:7b",
            "max_tokens": 200,
            "temperature": 0.3,
            "top_k": 2,
            "context_tokens": 600
        }
        
        self.generator = None
        self.initialized = False
        
    def initialize(self):
        """Initialize all RAG components"""
        log_message("=== RAG PIPELINE INITIALIZATION ===")
        
        try:
            # Import and initialize RAG generator
            from generate_response import RAGResponseGenerator
            
            log_message("Initializing RAG Response Generator...")
            self.generator = RAGResponseGenerator(
                ollama_host=self.config["ollama_host"],
                model_name=self.config["model_name"]
            )
            
            self.initialized = True
            log_message("✅ RAG Pipeline initialized successfully")
            return True
            
        except Exception as e:
            log_message(f"❌ RAG Pipeline initialization failed: {e}", "ERROR")
            return False
    
    def process_query(self, query, save_output=True):
        """
        Process a query through the complete RAG pipeline
        
        Args:
            query: User's question
            save_output: Whether to save response to file
            
        Returns:
            dict with complete pipeline result
        """
        
        if not self.initialized:
            log_message("❌ Pipeline not initialized", "ERROR")
            return {"success": False, "error": "Pipeline not initialized"}
        
        log_message(f"=== PROCESSING QUERY: {query} ===")
        pipeline_start = time.time()
        
        try:
            # Step 1: Generate RAG response
            log_message("🚀 Executing RAG pipeline...")
            result = self.generator.generate_response(
                query=query,
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"]
            )
            
            pipeline_time = time.time() - pipeline_start
            
            if result.get("success", False):
                log_message("✅ RAG pipeline completed successfully")
                
                # Add pipeline metadata
                result["pipeline_metadata"] = {
                    "pipeline_version": "US-004-Step-5",
                    "pipeline_time": pipeline_time,
                    "config": self.config,
                    "integration_flow": "US-002 → US-003 → Step-4 → Step-5"
                }
                
                # Save output if requested
                if save_output:
                    output_file = self._save_pipeline_result(result)
                    result["output_file"] = output_file
                
                return result
                
            else:
                log_message(f"❌ RAG pipeline failed: {result.get('error', 'Unknown error')}", "ERROR")
                return result
                
        except Exception as e:
            log_message(f"❌ Pipeline execution failed: {e}", "ERROR")
            return {
                "success": False,
                "error": f"Pipeline execution failed: {e}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    def _save_pipeline_result(self, result):
        """Save pipeline result to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"rag_pipeline_result_{timestamp}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            log_message(f"💾 Pipeline result saved to: {output_file}")
            return output_file
            
        except Exception as e:
            log_message(f"❌ Failed to save pipeline result: {e}", "ERROR")
            return None
    
    def display_pipeline_result(self, result):
        """Display pipeline result in formatted way"""
        print("\n" + "="*80)
        print("🤖 END-TO-END RAG PIPELINE RESULT")
        print("="*80)
        
        if not result.get("success", False):
            print(f"❌ PIPELINE FAILED: {result.get('error', 'Unknown error')}")
            return
        
        # Basic info
        print(f"📝 QUERY: {result['query']}")
        print(f"🕒 TIMESTAMP: {result['timestamp']}")
        print(f"🔄 PIPELINE VERSION: {result['pipeline_metadata']['pipeline_version']}")
        print(f"🔗 INTEGRATION FLOW: {result['pipeline_metadata']['integration_flow']}")
        
        # Performance metrics
        timing = result.get('timing', {})
        pipeline_time = result['pipeline_metadata']['pipeline_time']
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"  - Context Retrieval: {timing.get('context_retrieval', 0):.3f}s")
        print(f"  - LLM Generation: {timing.get('llm_generation', 0):.3f}s")
        print(f"  - Total RAG Time: {timing.get('total', 0):.3f}s")
        print(f"  - Pipeline Overhead: {pipeline_time - timing.get('total', 0):.3f}s")
        print(f"  - Total Pipeline Time: {pipeline_time:.3f}s")
        
        # Performance target check
        epic_target = 15.0
        if pipeline_time < epic_target:
            print(f"🎯 Epic Target: MET ({pipeline_time:.3f}s < {epic_target}s)")
        else:
            print(f"⚠️  Epic Target: MISSED ({pipeline_time:.3f}s > {epic_target}s)")
        
        # Context and sources
        print(f"\n📚 CONTEXT & SOURCES:")
        print(f"  - Documents Retrieved: {result.get('context_count', 0)}")
        print(f"  - Sources Used:")
        for i, source in enumerate(result.get('sources', []), 1):
            print(f"    {i}. {source}")
        
        # Response
        print(f"\n🎯 RAG RESPONSE:")
        print("-" * 80)
        print(result.get('response', 'No response'))
        print("-" * 80)
        
        # Technical details
        metadata = result.get('metadata', {})
        print(f"\n🔧 TECHNICAL DETAILS:")
        print(f"  - Model: {metadata.get('model', 'Unknown')}")
        print(f"  - Language: {metadata.get('language', 'Unknown')}")
        print(f"  - Temperature: {metadata.get('temperature', 0)}")
        print(f"  - Max Tokens: {metadata.get('max_tokens', 0)}")
        print(f"  - Prompt Length: {metadata.get('prompt_length', 0)} chars")
        print(f"  - Response Length: {metadata.get('response_length', 0)} chars")
        
        # Config used
        config = result['pipeline_metadata']['config']
        print(f"\n⚙️  PIPELINE CONFIG:")
        print(f"  - Ollama Host: {config['ollama_host']}")
        print(f"  - Model: {config['model_name']}")
        print(f"  - Max Tokens: {config['max_tokens']}")
        print(f"  - Temperature: {config['temperature']}")
        print(f"  - Top K: {config['top_k']}")
        print(f"  - Context Tokens: {config['context_tokens']}")
        
        # Output file
        if 'output_file' in result:
            print(f"\n💾 OUTPUT FILE: {result['output_file']}")

def run_pipeline_tests():
    """Run comprehensive pipeline tests"""
    log_message("=== RAG PIPELINE COMPREHENSIVE TESTS ===")
    
    # Test cases
    test_cases = [
        {
            "query": "AI tools for developers",
            "language": "english",
            "description": "English query about AI development tools"
        },
        {
            "query": "ChatGPT có những tính năng gì?",
            "language": "vietnamese", 
            "description": "Vietnamese query about ChatGPT features"
        },
        {
            "query": "NotebookLM research assistant",
            "language": "english",
            "description": "English query about NotebookLM"
        }
    ]
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    if not pipeline.initialize():
        log_message("❌ Pipeline initialization failed", "ERROR")
        return False
    
    # Run tests
    results = []
    for i, test_case in enumerate(test_cases, 1):
        log_message(f"\n--- Test Case {i}: {test_case['description']} ---")
        
        try:
            result = pipeline.process_query(test_case["query"], save_output=False)
            results.append(result)
            
            if result.get("success", False):
                timing = result.get('timing', {})
                pipeline_time = result['pipeline_metadata']['pipeline_time']
                log_message(f"✅ Test {i} PASSED - {pipeline_time:.3f}s total")
            else:
                log_message(f"❌ Test {i} FAILED - {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            log_message(f"❌ Test {i} ERROR - {e}")
            results.append({
                "success": False,
                "error": str(e),
                "query": test_case["query"]
            })
    
    # Summary
    log_message("\n=== TEST SUMMARY ===")
    passed = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    log_message(f"✅ Passed: {passed}/{total}")
    log_message(f"❌ Failed: {total - passed}/{total}")
    
    if passed > 0:
        successful_results = [r for r in results if r.get("success", False)]
        avg_time = sum(r['pipeline_metadata']['pipeline_time'] for r in successful_results) / len(successful_results)
        log_message(f"⚡ Average pipeline time: {avg_time:.3f}s")
        
        if avg_time < 15:
            log_message("🎯 Average performance meets Epic target")
        else:
            log_message("⚠️  Average performance exceeds Epic target")
    
    return passed == total

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="End-to-End RAG Pipeline - Step 5")
    parser.add_argument("query", nargs='?', help="User question to process")
    parser.add_argument("--test", action="store_true", help="Run comprehensive pipeline tests")
    parser.add_argument("--config", help="Path to pipeline configuration file")
    parser.add_argument("--save", action="store_true", default=True, help="Save pipeline result to file")
    
    args = parser.parse_args()
    
    print("🚀 End-to-End RAG Pipeline - Step 5")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load config if provided
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            log_message(f"✅ Configuration loaded from {args.config}")
        except Exception as e:
            log_message(f"❌ Failed to load config: {e}", "ERROR")
            return 1
    
    # Run tests if requested
    if args.test:
        success = run_pipeline_tests()
        return 0 if success else 1
    
    # Process single query
    if not args.query:
        print("❌ Please provide a query or use --test flag")
        print("Usage: python3.8 rag_pipeline.py \"Your question here\"")
        return 1
    
    # Initialize and run pipeline
    pipeline = RAGPipeline(config)
    
    if not pipeline.initialize():
        log_message("❌ Pipeline initialization failed", "ERROR")
        return 1
    
    # Process query
    result = pipeline.process_query(args.query, save_output=args.save)
    
    # Display result
    pipeline.display_pipeline_result(result)
    
    if result.get("success", False):
        log_message("✅ Step 5 completed successfully!")
        return 0
    else:
        log_message("❌ Step 5 failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 