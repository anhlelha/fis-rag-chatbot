# 🚀 Vector Database Implementation - US-003

**Epic**: 1 - Proof of Concept  
**User Story**: US-003 - Vector Database Implementation  
**Completion Date**: 2025-07-11  
**Status**: ✅ Completed Successfully

---

## 📋 Overview

This document provides comprehensive guidance for using the vector database implementation for the FIS Internal ChatBot RAG system. The implementation uses FAISS (Facebook AI Similarity Search) for efficient similarity search on document embeddings.

## 🏗️ Architecture

```
US-003 Vector Database Pipeline:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Documents     │ -> │   Embeddings    │ -> │  Vector Database│
│  (from US-002)  │    │ (sentence-bert) │    │     (FAISS)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      v
                                              ┌─────────────────┐
                                              │ Similarity Search│
                                              │   (Query API)   │
                                              └─────────────────┘
```

## 🔧 System Requirements

- **OS**: CentOS 8 (or compatible Linux)
- **Python**: 3.8+
- **Dependencies**:
  - sentence-transformers
  - faiss-cpu
  - numpy
  - torch

## 📁 File Structure

```
/opt/rag-copilot/
├── scripts/vector/
│   ├── install_dependencies_faiss_only.py    # Step 1: Install libraries
│   ├── embed_chunks.py                       # Step 3: Generate embeddings
│   ├── init_vector_db.py                     # Step 4: Create vector DB
│   └── query_vector_db.py                    # Step 5: Query database
├── db/
│   ├── vector_db.index                       # FAISS index file
│   ├── vector_db_metadata.json               # Database metadata
│   ├── embeddings_backup.npy                 # Embeddings backup
│   └── chunks_backup.pkl                     # Document chunks backup
└── output/
    └── embeddings/                           # Embedding generation output
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3.8 install sentence-transformers faiss-cpu numpy torch
```

### 2. Generate Embeddings (if not done)
```bash
python3.8 /opt/rag-copilot/scripts/vector/embed_chunks.py /opt/rag-copilot/output/AI-Starter-Kit_final_output/embedding_ready.json
```

### 3. Initialize Vector Database (if not done)
```bash
python3.8 /opt/rag-copilot/scripts/vector/init_vector_db.py /opt/rag-copilot/output/embeddings
```

### 4. Query Database
```bash
python3.8 /opt/rag-copilot/scripts/vector/query_vector_db.py "your search query" --timing
```

## 📖 Detailed Usage

### Query Examples

#### Basic Search
```bash
python3.8 /opt/rag-copilot/scripts/vector/query_vector_db.py "AI coding tools"
```

#### Performance Testing
```bash
python3.8 /opt/rag-copilot/scripts/vector/query_vector_db.py "ChatGPT features" --timing
```

#### Save Results
```bash
python3.8 /opt/rag-copilot/scripts/vector/query_vector_db.py "NotebookLM research" --save-results
```

### Expected Output Format

```
🔍 SEARCH QUERY: AI coding tools
================================================================================

📄 RESULT #1
   Document Index: 0
   Similarity Score: 0.8542
   Distance: 0.1706
   Content: 🚀 AI Starter Kit - Hướng dẫn sử dụng AI cho người mới bắt đầu...

📄 RESULT #2
   Document Index: 1
   Similarity Score: 0.7231
   Distance: 0.3891
   Content: 🤖 ChatGPT - Conversational AI...

⏱️  PERFORMANCE METRICS:
   Search time: 0.0023s
   Total time: 1.2340s
   Target: < 5.0s ✅ PASS
```

## 🔍 API Reference

### query_vector_db.py

**Usage**: `python3.8 query_vector_db.py <query> [options]`

**Parameters**:
- `query`: Search query text (required)
- `--timing`: Enable performance timing
- `--save-results`: Save results to JSON file

**Output**:
- Console display of search results
- Performance metrics (if --timing)
- JSON file (if --save-results)

## 📊 Performance Specifications

| Metric | Target | Achieved |
|--------|--------|----------|
| Search Time | < 5.0s | ~0.002s |
| Database Size | 4 vectors | ✅ |
| Embedding Dimension | 384 | ✅ |
| Index Type | FAISS IndexFlatL2 | ✅ |

## 🔧 Configuration

### Database Settings
- **Index Type**: IndexFlatL2 (exact search for small datasets)
- **Embedding Model**: all-MiniLM-L6-v2
- **Vector Dimension**: 384
- **Storage Format**: Binary FAISS index

### Customization Options

#### Change Embedding Model
Edit the model name in scripts:
```python
model = SentenceTransformer('all-MiniLM-L6-v2')  # Change this
```

#### Adjust Search Results
Modify the `k` parameter in query script:
```python
k = min(5, index.ntotal)  # Change 5 to desired number
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Index file not found"
```bash
# Solution: Run Step 4 first
python3.8 /opt/rag-copilot/scripts/vector/init_vector_db.py /opt/rag-copilot/output/embeddings
```

#### 2. "Embeddings directory not found"
```bash
# Solution: Run Step 3 first
python3.8 /opt/rag-copilot/scripts/vector/embed_chunks.py /opt/rag-copilot/output/AI-Starter-Kit_final_output/embedding_ready.json
```

#### 3. "Module not found" errors
```bash
# Solution: Install dependencies
pip3.8 install sentence-transformers faiss-cpu numpy torch
```

#### 4. Performance issues
- Check system resources (CPU, RAM)
- Consider using IndexIVFFlat for larger datasets
- Monitor disk I/O for database loading

### Debug Commands

#### Check Database Status
```bash
python3.8 -c "
import faiss, json, os
db_path = '/opt/rag-copilot/db/vector_db.index'
if os.path.exists(db_path):
    index = faiss.read_index(db_path)
    print(f'✅ Database OK: {index.ntotal} vectors')
else:
    print('❌ Database not found')
"
```

#### Verify Dependencies
```bash
python3.8 -c "import sentence_transformers, faiss, numpy, torch; print('✅ All dependencies OK')"
```

## 📈 Scaling Considerations

### For Larger Datasets (>1000 documents)

1. **Use IVF Index**:
   ```python
   # In init_vector_db.py, change:
   index_type = "IndexIVFFlat"
   ```

2. **Batch Processing**:
   ```python
   # Process embeddings in batches
   batch_size = 100
   ```

3. **Memory Management**:
   ```python
   # Use memory mapping for large indices
   faiss.write_index(index, "index.faiss")
   ```

## 🔗 Integration with Other Components

### US-002 Integration
- Input: `embedding_ready.json` from document processing
- Dependencies: Processed document chunks

### US-004 Integration (Future)
- Output: Search results for RAG pipeline
- API: Query interface for chat system

## 📝 Maintenance

### Regular Tasks

1. **Database Backup**:
   ```bash
   cp -r /opt/rag-copilot/db /opt/rag-copilot/db_backup_$(date +%Y%m%d)
   ```

2. **Performance Monitoring**:
   ```bash
   python3.8 /opt/rag-copilot/scripts/vector/query_vector_db.py "test query" --timing
   ```

3. **Update Documents**:
   - Re-run Steps 3-4 when new documents are added
   - Backup existing database before updates

### Monitoring Metrics

- Search response time (target: < 5s)
- Database file size
- Memory usage during queries
- Index loading time

## 🎯 Success Criteria

- [x] Vector database created successfully
- [x] Search functionality working
- [x] Performance targets met (< 5s)
- [x] Database persistence verified
- [x] Documentation completed

## 🚀 Next Steps

1. **US-004**: Integrate with RAG pipeline
2. **Optimization**: Scale for larger document sets
3. **Monitoring**: Implement production monitoring
4. **API**: Create REST API for queries

---

**Last Updated**: 2025-07-11  
**Version**: 1.0  
**Maintainer**: FIS Internal ChatBot Team 