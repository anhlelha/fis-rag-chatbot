#!/usr/bin/env python3.8
"""
RAG Response Generation - Step 4: Prompt Engineering & LLM Integration
Integrates context retrieval with Mistral 7B LLM via Ollama for final response generation.

Requirements from US-004 Step 4:
- Design RAG prompt template for Vietnamese/English
- Implement context injection with source citations  
- Mistral 7B response generation via Ollama

Usage:
    python3.8 generate_response.py "Quy trình nghỉ phép của công ty như thế nào?" --context-file context.json
    python3.8 generate_response.py "What is the expense reimbursement process?" --context-file context.json
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import ollama
    from retrieve_context import retrieve_context, setup_vector_db
    print("✅ All required modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required packages: pip3.8 install ollama sentence-transformers")
    sys.exit(1)

class RAGResponseGenerator:
    """
    RAG Response Generator integrating context retrieval with LLM generation
    """
    
    def __init__(self, ollama_host="http://localhost:11434", model_name="mistral:7b"):
        """Initialize RAG Response Generator"""
        self.ollama_host = ollama_host
        self.model_name = model_name
        self.client = None
        self.vector_db = None
        self.model = None
        
        # Initialize components
        self._setup_ollama_client()
        self._setup_vector_db()
        
    def _setup_ollama_client(self):
        """Setup Ollama client connection"""
        try:
            self.client = ollama.Client(host=self.ollama_host)
            # Test connection
            models = self.client.list()
            print(f"✅ Ollama client connected to {self.ollama_host}")
            
            # Handle different response formats
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
                print(f"Response type: {type(models)}")
                print(f"Response: {models}")
                sys.exit(1)
            
            # Extract model names
            model_names = []
            for m in model_list:
                model_name = None
                
                if hasattr(m, 'model'):
                    # Model object with .model attribute
                    model_name = m.model
                elif hasattr(m, 'name'):
                    # Model object with .name attribute
                    model_name = m.name
                elif isinstance(m, dict) and 'name' in m:
                    # Dictionary with 'name' key
                    model_name = m['name']
                elif isinstance(m, dict) and 'model' in m:
                    # Dictionary with 'model' key
                    model_name = m['model']
                else:
                    # Try to extract from string representation
                    model_str = str(m)
                    if "model='" in model_str:
                        # Extract from "model='mistral:7b'"
                        start = model_str.find("model='") + 7
                        end = model_str.find("'", start)
                        if end > start:
                            model_name = model_str[start:end]
                    else:
                        model_name = model_str
                
                if model_name:
                    model_names.append(model_name)
                else:
                    model_names.append('unknown')
            
            print(f"✅ Available models: {model_names}")
            
            # Verify our model exists
            model_found = any(self.model_name in name for name in model_names)
            
            if not model_found:
                print(f"❌ Model {self.model_name} not found!")
                print("Available models:")
                for name in model_names:
                    print(f"  - {name}")
                print(f"\nTo pull the model, run: ollama pull {self.model_name}")
                sys.exit(1)
            
            print(f"✅ Model {self.model_name} ready")
            
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("Make sure Ollama is running on localhost:11434")
            print("Check service status: systemctl status ollama")
            sys.exit(1)
    
    def _setup_vector_db(self):
        """Setup vector database and embedding model"""
        try:
            self.vector_db, self.model = setup_vector_db()
            print("✅ Vector database and embedding model loaded")
        except Exception as e:
            print(f"❌ Failed to setup vector DB: {e}")
            sys.exit(1)
    
    def _detect_language(self, text):
        """Simple language detection for Vietnamese vs English"""
        vietnamese_chars = 'àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
        vietnamese_count = sum(1 for char in text.lower() if char in vietnamese_chars)
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "english"
        
        vietnamese_ratio = vietnamese_count / total_chars
        return "vietnamese" if vietnamese_ratio > 0.1 else "english"
    
    def _create_rag_prompt(self, query, context_data, language="auto"):
        """
        Create RAG prompt template with context injection and source citations
        
        Args:
            query: User's question
            context_data: Retrieved context with sources
            language: "vietnamese", "english", or "auto"
        """
        
        if language == "auto":
            language = self._detect_language(query)
        
        # Format context with sources
        formatted_context = ""
        sources = []
        
        for i, ctx in enumerate(context_data, 1):
            source_info = f"Source {i}: {ctx.get('source', 'Unknown')}"
            if 'metadata' in ctx and ctx['metadata']:
                if 'title' in ctx['metadata']:
                    source_info += f" - {ctx['metadata']['title']}"
                if 'section' in ctx['metadata']:
                    source_info += f" (Section: {ctx['metadata']['section']})"
            
            formatted_context += f"\n--- {source_info} ---\n"
            formatted_context += ctx['content']
            formatted_context += f"\n(Relevance Score: {ctx.get('score', 0):.3f})\n"
            
            sources.append(source_info)
        
        if language == "vietnamese":
            prompt_template = f"""Bạn là một AI Assistant thông minh hỗ trợ nhân viên FIS Corporation. Hãy trả lời câu hỏi dựa trên thông tin được cung cấp.

NGUYÊN TẮC QUAN TRỌNG:
1. CHỈ sử dụng thông tin từ các tài liệu được cung cấp bên dưới
2. Nếu không tìm thấy thông tin liên quan, hãy nói rõ "Tôi không tìm thấy thông tin này trong tài liệu hiện có"
3. Luôn trích dẫn nguồn thông tin (Source 1, Source 2, etc.)
4. Trả lời bằng tiếng Việt một cách rõ ràng và chi tiết
5. Nếu có nhiều thông tin liên quan, hãy tổ chức thành các mục rõ ràng

THÔNG TIN TỪ TÀI LIỆU:
{formatted_context}

CÂU HỎI: {query}

TRẢ LỜI:"""

        else:  # English
            prompt_template = f"""You are an intelligent AI Assistant supporting FIS Corporation employees. Answer the question based on the provided information.

IMPORTANT PRINCIPLES:
1. ONLY use information from the documents provided below
2. If no relevant information is found, clearly state "I cannot find this information in the available documents"
3. Always cite information sources (Source 1, Source 2, etc.)
4. Answer in English clearly and in detail
5. If there are multiple relevant pieces of information, organize them into clear sections

INFORMATION FROM DOCUMENTS:
{formatted_context}

QUESTION: {query}

ANSWER:"""

        return prompt_template, sources
    
    def generate_response(self, query, max_tokens=1000, temperature=0.3):
        """
        Generate complete RAG response: Query → Context → LLM Response
        
        Args:
            query: User's question
            max_tokens: Maximum tokens for LLM response
            temperature: LLM temperature for creativity control
            
        Returns:
            dict with response, sources, timing, and metadata
        """
        
        start_time = time.time()
        print(f"\n🔍 Processing query: {query}")
        
        # Step 1: Retrieve relevant context (optimized for speed)
        print("📚 Retrieving relevant context...")
        context_retrieval_start = time.time()
        
        try:
            context_data = retrieve_context(
                query, 
                self.vector_db, 
                self.model, 
                top_k=2,         # Reduced from 3 for faster generation
                max_tokens=600   # Reduced from 2000 for faster LLM generation
            )
            
            context_retrieval_time = time.time() - context_retrieval_start
            print(f"✅ Context retrieved in {context_retrieval_time:.3f}s")
            print(f"📄 Found {len(context_data)} relevant documents")
            
        except Exception as e:
            print(f"❌ Context retrieval failed: {e}")
            return {
                "success": False,
                "error": f"Context retrieval failed: {e}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 2: Create RAG prompt with context injection
        print("📝 Creating RAG prompt...")
        try:
            prompt, sources = self._create_rag_prompt(query, context_data)
            print(f"✅ Prompt created with {len(sources)} sources")
            
        except Exception as e:
            print(f"❌ Prompt creation failed: {e}")
            return {
                "success": False,
                "error": f"Prompt creation failed: {e}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
        
        # Step 3: Generate response using Mistral 7B via Ollama
        print("🤖 Generating response with Mistral 7B...")
        llm_start_time = time.time()
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_k": 40,
                    "top_p": 0.9,
                    "stop": ["Human:", "User:", "Question:", "CÂU HỎI:"]
                }
            )
            
            llm_time = time.time() - llm_start_time
            total_time = time.time() - start_time
            
            print(f"✅ Response generated in {llm_time:.3f}s")
            print(f"⏱️  Total processing time: {total_time:.3f}s")
            
            # Format final response
            result = {
                "success": True,
                "query": query,
                "response": response['response'].strip(),
                "sources": sources,
                "context_count": len(context_data),
                "timing": {
                    "context_retrieval": context_retrieval_time,
                    "llm_generation": llm_time,
                    "total": total_time
                },
                "metadata": {
                    "model": self.model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "language": self._detect_language(query),
                    "prompt_length": len(prompt),
                    "response_length": len(response['response'])
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
            return {
                "success": False,
                "error": f"LLM generation failed: {e}",
                "query": query,
                "context_count": len(context_data) if 'context_data' in locals() else 0,
                "sources": sources if 'sources' in locals() else [],
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_from_context_file(self, query, context_file_path, max_tokens=1000, temperature=0.3):
        """
        Generate response using pre-saved context file
        
        Args:
            query: User's question
            context_file_path: Path to JSON file with context data
            max_tokens: Maximum tokens for LLM response
            temperature: LLM temperature
        """
        
        try:
            with open(context_file_path, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            print(f"📂 Loaded context from {context_file_path}")
            print(f"📄 Context contains {len(context_data)} documents")
            
        except Exception as e:
            print(f"❌ Failed to load context file: {e}")
            return {
                "success": False,
                "error": f"Failed to load context file: {e}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
        
        # Create prompt and generate response
        start_time = time.time()
        
        try:
            prompt, sources = self._create_rag_prompt(query, context_data)
            
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "num_predict": max_tokens,
                    "temperature": temperature,
                    "top_k": 40,
                    "top_p": 0.9,
                    "stop": ["Human:", "User:", "Question:", "CÂU HỎI:"]
                }
            )
            
            total_time = time.time() - start_time
            
            result = {
                "success": True,
                "query": query,
                "response": response['response'].strip(),
                "sources": sources,
                "context_count": len(context_data),
                "context_file": context_file_path,
                "timing": {
                    "total": total_time
                },
                "metadata": {
                    "model": self.model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "language": self._detect_language(query)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Response generation failed: {e}")
            return {
                "success": False,
                "error": f"Response generation failed: {e}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

def save_response(result, output_file=None):
    """Save response result to JSON file"""
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"rag_response_{timestamp}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 Response saved to {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Failed to save response: {e}")
        return None

def display_response(result):
    """Display response in a formatted way"""
    print("\n" + "="*80)
    print("🤖 RAG RESPONSE GENERATION RESULT")
    print("="*80)
    
    if not result["success"]:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        return
    
    print(f"📝 QUERY: {result['query']}")
    print(f"🕒 TIMESTAMP: {result['timestamp']}")
    print(f"⏱️  PROCESSING TIME: {result['timing']['total']:.3f}s")
    print(f"📚 CONTEXT SOURCES: {result['context_count']}")
    
    print(f"\n📖 SOURCES USED:")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source}")
    
    print(f"\n🎯 RESPONSE:")
    print("-" * 80)
    print(result['response'])
    print("-" * 80)
    
    if 'timing' in result and 'context_retrieval' in result['timing']:
        print(f"\n⚡ PERFORMANCE:")
        print(f"  - Context Retrieval: {result['timing']['context_retrieval']:.3f}s")
        print(f"  - LLM Generation: {result['timing']['llm_generation']:.3f}s")
        print(f"  - Total Time: {result['timing']['total']:.3f}s")
    
    print(f"\n🔧 METADATA:")
    print(f"  - Model: {result['metadata']['model']}")
    print(f"  - Language: {result['metadata']['language']}")
    print(f"  - Temperature: {result['metadata']['temperature']}")
    print(f"  - Prompt Length: {result['metadata']['prompt_length']} chars")
    print(f"  - Response Length: {result['metadata']['response_length']} chars")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="RAG Response Generation - Step 4")
    parser.add_argument("query", help="User question to process")
    parser.add_argument("--context-file", help="Path to pre-saved context JSON file")
    parser.add_argument("--output", help="Output file for response (JSON)")
    parser.add_argument("--model", default="mistral:7b", help="Ollama model name")
    parser.add_argument("--max-tokens", type=int, default=200, help="Maximum response tokens (reduced for speed)")
    parser.add_argument("--temperature", type=float, default=0.3, help="LLM temperature")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama host")
    
    args = parser.parse_args()
    
    print("🚀 RAG Response Generation - Step 4: Prompt Engineering & LLM Integration")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Query: {args.query}")
    print(f"🤖 Model: {args.model}")
    print(f"🌡️  Temperature: {args.temperature}")
    print(f"📏 Max Tokens: {args.max_tokens}")
    
    # Initialize RAG Response Generator
    try:
        generator = RAGResponseGenerator(
            ollama_host=args.host,
            model_name=args.model
        )
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        return 1
    
    # Generate response
    if args.context_file:
        print(f"📂 Using context file: {args.context_file}")
        result = generator.generate_from_context_file(
            args.query,
            args.context_file,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
    else:
        print("🔍 Using dynamic context retrieval")
        result = generator.generate_response(
            args.query,
            max_tokens=args.max_tokens,
            temperature=args.temperature
        )
    
    # Display and save results
    display_response(result)
    
    if args.output or result["success"]:
        output_file = save_response(result, args.output)
        if output_file and result["success"]:
            print(f"\n✅ Step 4 completed successfully!")
            print(f"📁 Response saved to: {output_file}")
            print(f"⏱️  Total time: {result['timing']['total']:.3f}s")
            
            # Performance check against Epic target (15s)
            if result['timing']['total'] < 15:
                print(f"🎯 Performance target MET: {result['timing']['total']:.3f}s < 15s")
            else:
                print(f"⚠️  Performance target MISSED: {result['timing']['total']:.3f}s > 15s")
    
    return 0 if result["success"] else 1

if __name__ == "__main__":
    sys.exit(main()) 