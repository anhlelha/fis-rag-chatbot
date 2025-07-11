# Step 4: RAG Response Generation - Usage Guide

## Overview
Step 4 implements **Prompt Engineering & LLM Integration** for the RAG pipeline, combining context retrieval with Mistral 7B LLM to generate intelligent responses.

## Files Created
- `generate_response.py` - Main RAG response generation script
- `test_step4.py` - Test suite for validation
- `quick_test_step4.py` - Quick validation script
- `debug_ollama.py` - Ollama connection debug script
- `check_dependencies.py` - Dependency checker
- `README_step4.md` - This usage guide

## Features
- ✅ Bilingual prompt templates (Vietnamese/English)
- ✅ Context injection with source citations
- ✅ Mistral 7B integration via Ollama
- ✅ Dynamic context retrieval or pre-saved context files
- ✅ Performance monitoring and Epic target validation
- ✅ Comprehensive error handling and logging

## Usage Examples

### 1. Basic RAG Response Generation
```bash
# Vietnamese query with dynamic context retrieval
python3.8 generate_response.py "Quy trình nghỉ phép của công ty như thế nào?" --max-tokens 500

# English query with custom settings
python3.8 generate_response.py "What is the expense reimbursement process?" --max-tokens 800 --temperature 0.2
```

### 2. Using Pre-saved Context Files
```bash
# Generate response using pre-saved context
python3.8 generate_response.py "Quy trình nghỉ phép như thế nào?" --context-file context.json --output response.json
```

### 3. Custom Configuration
```bash
# Custom Ollama host and model
python3.8 generate_response.py "How do I apply for training?" --host http://192.168.1.100:11434 --model mistral:7b --max-tokens 1000
```

### 4. Run Test Suite
```bash
# Quick validation (recommended)
python3.8 quick_test_step4.py

# Full test suite (if imports work)
python3.8 test_step4.py
```

### 5. Debug Issues
```bash
# Check dependencies
python3.8 check_dependencies.py

# Debug Ollama connection
python3.8 debug_ollama.py
```

## Command Line Options

### generate_response.py
- `query` - User question to process (required)
- `--context-file` - Path to pre-saved context JSON file
- `--output` - Output file for response (JSON format)
- `--model` - Ollama model name (default: mistral:7b)
- `--max-tokens` - Maximum response tokens (default: 1000)
- `--temperature` - LLM temperature (default: 0.3)
- `--host` - Ollama host URL (default: http://localhost:11434)

## Expected Output Format

### Success Response
```json
{
  "success": true,
  "query": "Quy trình nghỉ phép của công ty như thế nào?",
  "response": "Dựa trên thông tin từ tài liệu...",
  "sources": [
    "Source 1: RAG_Internal_AI_Copilot.md - Company Policies",
    "Source 2: employee_handbook.md - Leave Process"
  ],
  "context_count": 3,
  "timing": {
    "context_retrieval": 0.045,
    "llm_generation": 2.156,
    "total": 2.201
  },
  "metadata": {
    "model": "mistral:7b",
    "language": "vietnamese",
    "temperature": 0.3,
    "max_tokens": 500,
    "prompt_length": 1234,
    "response_length": 456
  },
  "timestamp": "2025-07-11T17:15:30.123456"
}
```

## Performance Targets
- **Epic Target**: < 15 seconds total processing time
- **Context Retrieval**: < 1 second (typically ~0.05s)
- **LLM Generation**: < 10 seconds (typically 2-5s)
- **Total Pipeline**: < 15 seconds

## Validation Steps

### 1. Prerequisites Check
```bash
# Check dependencies
python3.8 check_dependencies.py

# Check Ollama service
curl http://localhost:11434/api/tags

# Install missing dependencies if needed
pip3.8 install ollama sentence-transformers faiss-cpu numpy
```

### 2. Quick Test
```bash
# Run quick test (recommended)
python3.8 quick_test_step4.py

# Or run full test suite
python3.8 test_step4.py
```

### 3. Manual Validation
```bash
# Test Vietnamese query
python3.8 generate_response.py "Quy trình nghỉ phép như thế nào?" --max-tokens 300

# Test English query  
python3.8 generate_response.py "What is the leave process?" --max-tokens 300
```

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed
```
❌ Failed to connect to Ollama: 'name' or Connection refused
```
**Solution**: 
- Run debug script: `python3.8 debug_ollama.py`
- Check Ollama service: `systemctl status ollama`
- Start if needed: `sudo systemctl start ollama`
- Verify port: `netstat -tlnp | grep 11434`

#### 2. Model Not Found
```
❌ Model mistral:7b not found!
```
**Solution**:
- List available models: `ollama list`
- Pull model if needed: `ollama pull mistral:7b`

#### 3. Import Error
```
❌ Import error: No module named 'ollama'
```
**Solution**:
- Install dependencies: `pip3.8 install ollama sentence-transformers faiss-cpu`

#### 4. Context Retrieval Failed
```
❌ Context retrieval failed: No module named 'retrieve_context'
```
**Solution**:
- Make sure `retrieve_context.py` is in the same directory
- Check Step 3 completion

#### 5. Performance Issues
```
⚠️ Performance target MISSED: 18.5s > 15s
```
**Solution**:
- Reduce `max_tokens` parameter
- Check server resources (CPU/RAM)
- Optimize context retrieval (reduce `top_k`)

## Integration with Previous Steps

### Step 3 Dependencies
- `retrieve_context.py` - Context retrieval functionality
- `setup_vector_db()` - Vector database initialization
- FAISS index files and embedding model

### Data Flow
```
User Query → Language Detection → Context Retrieval (Step 3) → 
Prompt Engineering → LLM Generation → Response Formatting → Output
```

## Next Steps
After Step 4 completion, proceed to:
- **Step 5**: End-to-End RAG Pipeline Integration
- **Step 6**: API Interface & Web Service
- **Step 7**: Performance Testing & Optimization

## Files Generated
- `rag_response_YYYYMMDD_HHMMSS.json` - Individual response files
- `step4_test_results_YYYYMMDD_HHMMSS.json` - Test suite results

## Performance Monitoring
The script automatically tracks:
- Context retrieval time
- LLM generation time  
- Total processing time
- Performance target compliance (< 15s)
- Token usage and response quality metrics 