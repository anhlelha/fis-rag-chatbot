#!/usr/bin/env python3.8
"""
US-004 Step 3: Context Retrieval & Ranking
Retrieve relevant context from vector search and manage token limits for LLM
"""

import sys
import os
import json
import argparse
import numpy as np
from datetime import datetime

# Import for vector database and embeddings
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

def log_message(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def estimate_tokens(text):
    """Simple token estimation (1 token ≈ 4 characters for Vietnamese/English)"""
    return len(text) // 4

def setup_vector_db():
    """
    Setup vector database and embedding model for context retrieval
    Returns: (vector_db, embedding_model)
    """
    log_message("Setting up vector database and embedding model...")
    
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("Required dependencies not available. Please install: pip3.8 install faiss-cpu sentence-transformers")
    
    try:
        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        log_message("✅ Embedding model loaded: all-MiniLM-L6-v2")
        
        # Load FAISS index (from US-003 completion)
        vector_db_path = "/opt/rag-copilot/db/vector_db.index"
        
        if not os.path.exists(vector_db_path):
            raise FileNotFoundError(f"Vector database not found: {vector_db_path}")
        
        vector_db = faiss.read_index(vector_db_path)
        log_message(f"✅ Vector database loaded: {vector_db.ntotal} vectors")
        
        return vector_db, model
        
    except Exception as e:
        log_message(f"❌ Failed to setup vector database: {str(e)}", "ERROR")
        raise

def retrieve_context(query, vector_db, model, top_k=3, max_tokens=2000):
    """
    Retrieve relevant context for a query using vector similarity search
    
    Args:
        query: User's question
        vector_db: FAISS vector database
        model: Sentence transformer model
        top_k: Number of top results to return
        max_tokens: Maximum tokens for context
    
    Returns:
        List of context dictionaries with content, score, source, metadata
    """
    log_message(f"Retrieving context for query: {query}")
    log_message(f"Parameters: top_k={top_k}, max_tokens={max_tokens}")
    
    try:
        # Generate query embedding
        query_embedding = model.encode([query])
        log_message("✅ Query embedding generated")
        
        # Search vector database
        scores, indices = vector_db.search(query_embedding, top_k)
        log_message(f"✅ Vector search completed: {len(indices[0])} results")
        
        # Load document chunks (from US-003 completion)
        chunks_path = "/opt/rag-copilot/db/chunks_backup.pkl"
        
        if not os.path.exists(chunks_path):
            log_message("⚠️  Document chunks not found, using basic format", "WARNING")
            chunks = []
        else:
            import pickle
            with open(chunks_path, 'rb') as f:
                chunks = pickle.load(f)
            log_message(f"✅ Document chunks loaded: {len(chunks)} chunks")
        
        # Format results
        contexts = []
        total_tokens = 0
        
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx == -1:  # Invalid index
                continue
                
            # Get document chunk (US-003 format: list of strings)
            if idx < len(chunks):
                chunk = chunks[idx]
                
                # Handle different chunk formats
                if isinstance(chunk, str):
                    # US-003 format: list of strings
                    content = chunk
                    source = f'Document_{idx}'
                    metadata = {}
                elif isinstance(chunk, dict):
                    # Dictionary format
                    content = chunk.get('content', f'Document {idx} content')
                    source = chunk.get('source', f'Document_{idx}')
                    metadata = chunk.get('metadata', {})
                else:
                    # Fallback
                    content = str(chunk)
                    source = f'Document_{idx}'
                    metadata = {}
            else:
                content = f'Document {idx} content'
                source = f'Document_{idx}'
                metadata = {}
            
            # Estimate tokens for this content
            content_tokens = estimate_tokens(content)
            
            # Check if adding this content exceeds token limit
            if total_tokens + content_tokens > max_tokens:
                # Try to fit partial content
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 100:  # Only if meaningful space left
                    chars_that_fit = remaining_tokens * 4
                    truncated_content = content[:chars_that_fit] + "..."
                    
                    context = {
                        'content': truncated_content,
                        'score': float(score),
                        'source': source,
                        'metadata': {
                            'title': metadata.get('title', ''),
                            'section': metadata.get('section', ''),
                            'document_id': idx,
                            'truncated': True
                        }
                    }
                    contexts.append(context)
                    total_tokens += remaining_tokens
                    log_message(f"   Added truncated context {i+1}: {remaining_tokens} tokens")
                break
            else:
                context = {
                    'content': content,
                    'score': float(score),
                    'source': source,
                    'metadata': {
                        'title': metadata.get('title', ''),
                        'section': metadata.get('section', ''),
                        'document_id': idx,
                        'truncated': False
                    }
                }
                contexts.append(context)
                total_tokens += content_tokens
                log_message(f"   Added context {i+1}: {content_tokens} tokens (Score: {score:.3f})")
        
        log_message(f"✅ Context retrieval completed")
        log_message(f"   Retrieved contexts: {len(contexts)}")
        log_message(f"   Total tokens: {total_tokens}/{max_tokens}")
        
        return contexts
        
    except Exception as e:
        log_message(f"❌ Context retrieval failed: {str(e)}", "ERROR")
        raise

def retrieve_context_from_query_results(results_file, top_k=3, max_tokens=2000):
    """Retrieve and rank context from query processing results"""
    log_message(f"Loading query results from: {results_file}")
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            query_data = json.load(f)
        
        query = query_data.get('query', '')
        language = query_data.get('language', 'unknown')
        results = query_data.get('results', [])
        
        log_message(f"✅ Query results loaded")
        log_message(f"   Query: {query}")
        log_message(f"   Language: {language}")
        log_message(f"   Total results: {len(results)}")
        
        return query, language, results
        
    except Exception as e:
        log_message(f"❌ Failed to load query results: {str(e)}", "ERROR")
        return None, None, None

def rank_contexts_by_relevance(results, query, top_k=3):
    """Rank contexts by relevance score and content quality"""
    log_message(f"Ranking contexts by relevance (top {top_k})...")
    
    try:
        # Filter out results without content
        valid_results = [r for r in results if r.get('content')]
        
        if not valid_results:
            log_message("❌ No valid results with content found", "ERROR")
            return []
        
        # Sort by similarity score (descending)
        ranked_results = sorted(valid_results, key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        # Take top K
        top_results = ranked_results[:top_k]
        
        log_message(f"✅ Context ranking completed")
        log_message(f"   Valid results: {len(valid_results)}")
        log_message(f"   Top {top_k} selected")
        
        # Log ranking details
        for i, result in enumerate(top_results):
            log_message(f"   Rank {i+1}: Score {result.get('similarity_score', 0):.4f}")
        
        return top_results
        
    except Exception as e:
        log_message(f"❌ Context ranking failed: {str(e)}", "ERROR")
        return []

def manage_context_window(ranked_results, max_tokens=2000):
    """Manage context to fit within token limits"""
    log_message(f"Managing context window (max {max_tokens} tokens)...")
    
    try:
        final_contexts = []
        total_tokens = 0
        
        for result in ranked_results:
            content = result.get('content', '')
            content_tokens = estimate_tokens(content)
            
            # Check if adding this content exceeds token limit
            if total_tokens + content_tokens <= max_tokens:
                final_contexts.append(result)
                total_tokens += content_tokens
                log_message(f"   Added context {len(final_contexts)}: {content_tokens} tokens")
            else:
                # Try to fit partial content
                remaining_tokens = max_tokens - total_tokens
                if remaining_tokens > 100:  # Only if meaningful space left
                    # Estimate characters that fit
                    chars_that_fit = remaining_tokens * 4
                    truncated_content = content[:chars_that_fit] + "..."
                    
                    truncated_result = result.copy()
                    truncated_result['content'] = truncated_content
                    truncated_result['truncated'] = True
                    
                    final_contexts.append(truncated_result)
                    total_tokens += remaining_tokens
                    log_message(f"   Added truncated context {len(final_contexts)}: {remaining_tokens} tokens")
                
                break
        
        log_message(f"✅ Context window managed")
        log_message(f"   Final contexts: {len(final_contexts)}")
        log_message(f"   Total tokens: {total_tokens}/{max_tokens}")
        
        return final_contexts, total_tokens
        
    except Exception as e:
        log_message(f"❌ Context window management failed: {str(e)}", "ERROR")
        return [], 0

def format_context_for_llm(query, language, contexts, total_tokens):
    """Format context in a structure suitable for LLM prompt"""
    log_message("Formatting context for LLM...")
    
    try:
        # Create structured context
        formatted_context = {
            'query': query,
            'language': language,
            'context_summary': {
                'total_documents': len(contexts),
                'total_tokens': total_tokens,
                'retrieval_timestamp': datetime.now().isoformat()
            },
            'contexts': []
        }
        
        for i, context in enumerate(contexts):
            formatted_ctx = {
                'document_id': i + 1,
                'similarity_score': context.get('similarity_score', 0),
                'content': context.get('content', ''),
                'truncated': context.get('truncated', False),
                'metadata': context.get('metadata', {})
            }
            formatted_context['contexts'].append(formatted_ctx)
        
        # Create text version for LLM prompt
        text_context = f"Query: {query}\n"
        text_context += f"Language: {language}\n"
        text_context += f"Retrieved {len(contexts)} relevant documents:\n\n"
        
        for i, context in enumerate(contexts):
            text_context += f"Document {i+1} (Relevance: {context.get('similarity_score', 0):.3f}):\n"
            text_context += f"{context.get('content', '')}\n"
            text_context += "---\n"
        
        log_message(f"✅ Context formatted for LLM")
        log_message(f"   Structured format: {len(formatted_context['contexts'])} documents")
        log_message(f"   Text format: {estimate_tokens(text_context)} tokens")
        
        return formatted_context, text_context
        
    except Exception as e:
        log_message(f"❌ Context formatting failed: {str(e)}", "ERROR")
        return None, None

def save_context_data(formatted_context, text_context, output_file):
    """Save formatted context data"""
    log_message(f"Saving context data to: {output_file}")
    
    try:
        context_data = {
            'structured_context': formatted_context,
            'text_context': text_context,
            'token_estimate': estimate_tokens(text_context),
            'created_at': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(context_data, f, indent=2, ensure_ascii=False)
        
        log_message(f"✅ Context data saved")
        return True
        
    except Exception as e:
        log_message(f"❌ Failed to save context data: {str(e)}", "ERROR")
        return False

def main():
    """Main context retrieval and ranking function"""
    log_message("=== US-004 STEP 3: CONTEXT RETRIEVAL & RANKING ===")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Retrieve and rank context for LLM')
    parser.add_argument('query', help='User question')
    parser.add_argument('--top-k', type=int, default=3, help='Number of top results to retrieve')
    parser.add_argument('--max-tokens', type=int, default=2000, help='Maximum tokens for context')
    parser.add_argument('--results-file', help='Query results file (if available)')
    
    args = parser.parse_args()
    
    # If no results file provided, run query processing first
    if not args.results_file:
        log_message("No results file provided, running query processing first...")
        
        # Run Step 2 script
        import subprocess
        cmd = ['python3.8', '/opt/rag-copilot/scripts/rag/process_query.py', args.query]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                log_message(f"❌ Query processing failed: {result.stderr}", "ERROR")
                sys.exit(1)
            
            # Find the latest results file
            import glob
            results_files = glob.glob('/tmp/query_results_*.json')
            if not results_files:
                log_message("❌ No query results file found", "ERROR")
                sys.exit(1)
            
            args.results_file = max(results_files)  # Latest file
            log_message(f"✅ Using query results: {args.results_file}")
            
        except Exception as e:
            log_message(f"❌ Failed to run query processing: {str(e)}", "ERROR")
            sys.exit(1)
    
    # Step 1: Load query results
    query, language, results = retrieve_context_from_query_results(args.results_file, args.top_k, args.max_tokens)
    if not results:
        log_message("❌ Failed to load query results", "ERROR")
        sys.exit(1)
    
    # Step 2: Rank contexts by relevance
    ranked_contexts = rank_contexts_by_relevance(results, query, args.top_k)
    if not ranked_contexts:
        log_message("❌ No ranked contexts available", "ERROR")
        sys.exit(1)
    
    # Step 3: Manage context window
    final_contexts, total_tokens = manage_context_window(ranked_contexts, args.max_tokens)
    if not final_contexts:
        log_message("❌ No contexts fit within token limit", "ERROR")
        sys.exit(1)
    
    # Step 4: Format context for LLM
    formatted_context, text_context = format_context_for_llm(query, language, final_contexts, total_tokens)
    if not formatted_context:
        log_message("❌ Context formatting failed", "ERROR")
        sys.exit(1)
    
    # Step 5: Save context data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"/tmp/context_{timestamp}.json"
    
    if not save_context_data(formatted_context, text_context, output_file):
        log_message("❌ Failed to save context data", "ERROR")
        sys.exit(1)
    
    # Step 6: Display context summary
    print("\n" + "="*80)
    print(f"📋 CONTEXT RETRIEVAL SUMMARY")
    print("="*80)
    print(f"Query: {query}")
    print(f"Language: {language}")
    print(f"Documents retrieved: {len(final_contexts)}")
    print(f"Total tokens: {total_tokens}/{args.max_tokens}")
    print(f"Context saved: {output_file}")
    print()
    
    print("📄 RETRIEVED CONTEXTS:")
    for i, ctx in enumerate(final_contexts):
        print(f"Document {i+1} (Score: {ctx.get('similarity_score', 0):.3f}):")
        content = ctx.get('content', '')[:200]
        print(f"  {content}{'...' if len(ctx.get('content', '')) > 200 else ''}")
        if ctx.get('truncated'):
            print("  [TRUNCATED TO FIT TOKEN LIMIT]")
        print()
    
    # Success summary
    log_message("=== STEP 3 COMPLETED SUCCESSFULLY ===")
    log_message(f"✅ Context retrieved: {len(final_contexts)} documents")
    log_message(f"✅ Token management: {total_tokens}/{args.max_tokens} tokens")
    log_message(f"✅ Context formatted for LLM")
    log_message(f"✅ Context saved: {output_file}")
    log_message("")
    log_message("🚀 Ready for Step 4: Prompt Engineering & LLM Integration")

if __name__ == "__main__":
    main() 