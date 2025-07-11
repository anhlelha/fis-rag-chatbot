# 📚 US-002 Document Processing Pipeline - Commands Reference

**Epic**: 1 - Proof of Concept  
**User Story**: US-002 - Document Processing Pipeline  
**Created**: 2025-07-10  
**Last Updated**: 2025-07-10 16:50

---

## 🐍 **Python Environment**

### **Check Python Versions**
```bash
# Check Python 3.8 installation
python3.8 --version
pip3.8 --version

# Check Python 3.6 (system)
python3 --version
pip3 --version
```

### **Install Required Libraries**
```bash
# Install for Python 3.8
pip3.8 install langchain pypdf python-docx pandas openpyxl

# Check installed packages
pip3.8 list | grep -E 'langchain|pypdf|python-docx|pandas|openpyxl'
```

---

## 📄 **Document Processing Commands**

### **Step 3: Process Markdown Files**
```bash
# Process a single MD file
python3.8 /opt/rag-copilot/scripts/process_md.py /path/to/file.md

# Check output
ls -la /opt/rag-copilot/output/
head -50 /opt/rag-copilot/output/filename_processed.json
```

### **Check Processing Results**
```bash
# Quick stats check
python3.8 -c "
import json
data = json.load(open('/opt/rag-copilot/output/AI-Starter-Kit_processed.json'))
stats = data['stats']
metadata = data['metadata']
print('=== PROCESSING RESULTS ===')
print(f'Title: {metadata[\"title\"]}')
print(f'File size: {metadata[\"file_size\"]} bytes')
print(f'Words: {stats[\"words\"]}')
print(f'Headings: {stats[\"headings_count\"]}')
print(f'Clean content: {len(data[\"clean_content\"])} chars')
"
```

---

## ✂️ **Text Chunking Commands**

### **Step 4: Simple Chunking**
```bash
# Run simple chunking script
python3.8 /opt/rag-copilot/scripts/simple_chunk.py /opt/rag-copilot/output/AI-Starter-Kit_processed.json

# Check chunking results
python3.8 -c "
import json
data = json.load(open('/opt/rag-copilot/output/AI-Starter-Kit_simple_chunked.json'))
stats = data['stats']
print('=== CHUNKING RESULTS ===')
print(f'Total chunks: {stats[\"total_chunks\"]}')
print(f'Average tokens/chunk: {stats[\"avg_tokens_per_chunk\"]}')
print(f'Min tokens: {stats[\"min_tokens\"]}')
print(f'Max tokens: {stats[\"max_tokens\"]}')
print(f'Total tokens: {stats[\"total_tokens\"]}')
"
```

### **Preview Chunks**
```bash
# Show first 3 chunks
python3.8 -c "
import json
data = json.load(open('/opt/rag-copilot/output/AI-Starter-Kit_simple_chunked.json'))
chunks = data['chunks']
print('=== CHUNKS PREVIEW ===')
for i, chunk in enumerate(chunks[:3]):
    print(f'\nChunk {i+1} ({chunk[\"tokens\"]} tokens):')
    preview = chunk['content'][:150]
    print(f'{preview}...')
    print('-' * 50)
"
```

### **Check Specific Chunk**
```bash
# Show chunk by ID (replace X with chunk number)
python3.8 -c "
import json
data = json.load(open('/opt/rag-copilot/output/AI-Starter-Kit_simple_chunked.json'))
chunk_id = 1  # Change this number
chunk = data['chunks'][chunk_id - 1]
print(f'=== CHUNK {chunk_id} ===')
print(f'Tokens: {chunk[\"tokens\"]}')
print(f'Words: {chunk[\"words\"]}')
print(f'Chars: {chunk[\"chars\"]}')
print(f'Content:')
print(chunk['content'])
"
```

---

## 📊 **File Management Commands**

### **Directory Structure**
```bash
# Check project structure
tree /opt/rag-copilot/

# Or if tree not available
find /opt/rag-copilot/ -type d
find /opt/rag-copilot/ -type f -name "*.py"
find /opt/rag-copilot/ -type f -name "*.json"
```

### **File Operations**
```bash
# List all output files
ls -la /opt/rag-copilot/output/

# Check file sizes
du -h /opt/rag-copilot/output/*

# Count lines in JSON files
wc -l /opt/rag-copilot/output/*.json
```

### **Backup Important Files**
```bash
# Backup processed files
cp /opt/rag-copilot/output/*.json /opt/rag-copilot/backup/

# Archive results
tar -czf rag-results-$(date +%Y%m%d).tar.gz /opt/rag-copilot/output/
```

---

## 🔍 **Debugging Commands**

### **Check JSON File Validity**
```bash
# Validate JSON syntax
python3.8 -m json.tool /opt/rag-copilot/output/filename.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

### **Check Text Encoding**
```bash
# Check file encoding
file -i /opt/rag-copilot/output/*.json

# Check for problematic characters
python3.8 -c "
import json
data = json.load(open('/opt/rag-copilot/output/AI-Starter-Kit_processed.json'))
content = data['clean_content']
print('Non-ASCII chars:', len([c for c in content if ord(c) > 127]))
print('Total chars:', len(content))
"
```

### **Memory and Performance**
```bash
# Check disk usage
df -h /opt/rag-copilot/

# Check memory usage during processing
free -h

# Time the processing
time python3.8 /opt/rag-copilot/scripts/process_md.py /path/to/file.md
```

---

## 🚀 **Quick Start Commands**

### **Full Pipeline Run**
```bash
# Complete processing pipeline for one file
FILE_PATH="/path/to/your/document.md"

# Step 1: Process MD file
python3.8 /opt/rag-copilot/scripts/process_md.py "$FILE_PATH"

# Step 2: Simple chunking
PROCESSED_FILE="/opt/rag-copilot/output/$(basename "$FILE_PATH" .md)_processed.json"
python3.8 /opt/rag-copilot/scripts/simple_chunk.py "$PROCESSED_FILE"

# Step 3: Check results
CHUNKED_FILE="/opt/rag-copilot/output/$(basename "$FILE_PATH" .md)_simple_chunked.json"
echo "Results saved to: $CHUNKED_FILE"
ls -la "$CHUNKED_FILE"
```

### **Batch Processing Multiple Files**
```bash
# Process all MD files in a directory
for file in /path/to/docs/*.md; do
    echo "Processing: $file"
    python3.8 /opt/rag-copilot/scripts/process_md.py "$file"
    
    # Get processed filename
    processed_file="/opt/rag-copilot/output/$(basename "$file" .md)_processed.json"
    
    # Chunk the processed file
    python3.8 /opt/rag-copilot/scripts/simple_chunk.py "$processed_file"
    
    echo "Completed: $file"
    echo "---"
done
```

---

## ⚠️ **Troubleshooting**

### **Common Issues**

**1. ModuleNotFoundError:**
```bash
# Ensure using Python 3.8
which python3.8
python3.8 -c "import sys; print(sys.version)"

# Reinstall packages if needed
pip3.8 install --upgrade langchain pypdf python-docx pandas openpyxl
```

**2. Permission Denied:**
```bash
# Fix script permissions
chmod +x /opt/rag-copilot/scripts/*.py

# Fix directory permissions
chmod 755 /opt/rag-copilot/output/
```

**3. File Not Found:**
```bash
# Check file exists and path is correct
ls -la /path/to/your/file.md
pwd  # Check current directory
```

**4. Memory Issues:**
```bash
# Check available memory
free -h

# Monitor memory usage
top -p $(pgrep python3.8)
```

**5. Line Endings Error (Windows → Linux):**
```bash
# Error: /usr/bin/env: 'python3.8\r': No such file or directory
# Solution: Fix line endings
cd /opt/rag-copilot/scripts
sed -i 's/\r$//' *.py
chmod +x *.py

# Or use the fix script
bash /path/to/fix_line_endings.sh
```

**6. Shebang Issues:**
```bash
# Fix shebang lines in all Python scripts
cd /opt/rag-copilot/scripts
for file in *.py; do
    sed -i '1s|.*|#!/usr/bin/env python3.8|' "$file"
done
```

---

## 💾 **Data Storage & Output Files (Step 6)**

### **Save Processed Data**
```bash
# Run data storage script
python3.8 /opt/rag-copilot/scripts/save_processed_data.py /opt/rag-copilot/output/AI-Starter-Kit_with_metadata.json

# Check output directory
ls -la /opt/rag-copilot/output/AI-Starter-Kit_final_output/
```

### **📁 Chi tiết 6 Files được tạo ra**

#### **1. `AI-Starter-Kit_complete.json` - Complete Data File**
```json
{
  "enhanced_chunks": [...],
  "metadata_stats": {...},
  "original_metadata": {...}
}
```
- **Mục đích**: Lưu trữ toàn bộ dữ liệu đã xử lý
- **Nội dung**: Tất cả chunks với metadata đầy đủ, thống kê, metadata gốc
- **Sử dụng**: Backup chính, có thể load lại để tiếp tục xử lý
- **Kích thước**: Lớn nhất (~50-100KB)
- **Ai sử dụng**: Developers cho debugging, reprocessing

#### **2. `chunks_summary.csv` - Human-Readable Analysis**
```csv
chunk_id,content_type,tokens,words,section,keywords_preview,content_preview
chunk_0,instruction,245,180,Introduction,"setup,install,guide","This guide will help you..."
chunk_1,overview,312,225,Overview,"features,benefits,usage","The AI Starter Kit provides..."
```
- **Mục đích**: Phân tích và review bằng mắt người
- **Nội dung**: Bảng tóm tắt dễ đọc với Excel/Google Sheets
- **Sử dụng**: Quality check, content analysis, stakeholder review
- **Đặc điểm**: Có thể sort, filter, analyze trong spreadsheet
- **Ai sử dụng**: Business users, content reviewers

#### **3. `embedding_ready.json` - Sẵn sàng cho US-003** ⭐ **QUAN TRỌNG NHẤT**
```json
{
  "documents": ["text chunk 1", "text chunk 2", ...],
  "metadata": [{"chunk_id": "...", "source_file": "...", ...}],
  "ids": ["chunk_0", "chunk_1", ...]
}
```
- **Mục đích**: **Input chính cho US-003 Vector Embedding**
- **Nội dung**: Format chuẩn cho embedding models
- **Sử dụng**: Trực tiếp feed vào sentence-transformers hoặc OpenAI embeddings
- **Đặc điểm**: Clean text, unique IDs, structured metadata
- **Ai sử dụng**: **US-003 Pipeline** - file này là bridge giữa US-002 và US-003

#### **4. `search_index.json` - Search Optimization**
```json
{
  "keyword_index": {
    "setup": ["chunk_0", "chunk_2"],
    "install": ["chunk_0", "chunk_1"]
  },
  "content_type_index": {
    "instruction": ["chunk_0", "chunk_3"],
    "overview": ["chunk_1"]
  },
  "chunks_by_section": {...}
}
```
- **Mục đích**: Tối ưu hóa tìm kiếm và retrieval
- **Nội dung**: Index theo keywords, content type, sections
- **Sử dụng**: Fast keyword search, content filtering
- **Đặc điểm**: Pre-computed indexes cho performance
- **Ai sử dụng**: Search engine, retrieval systems

#### **5. `processed_data.pkl` - Fast Loading Backup**
```python
# Binary pickle format
{
  "enhanced_chunks": [...],
  "metadata_stats": {...},
  "original_metadata": {...}
}
```
- **Mục đích**: Load nhanh nhất cho Python scripts
- **Nội dung**: Giống complete.json nhưng binary format
- **Sử dụng**: Development, debugging, fast reprocessing
- **Đặc điểm**: Load 5-10x nhanh hơn JSON
- **Ai sử dụng**: Python scripts, development tools

#### **6. `processing_report.json` - Summary Report**
```json
{
  "processing_summary": {
    "total_chunks": 4,
    "total_tokens": 1847,
    "avg_tokens_per_chunk": 461
  },
  "content_analysis": {
    "content_type_distribution": {...},
    "top_keywords": [...]
  },
  "ready_for_embedding": {
    "status": "ready",
    "next_steps": [...]
  }
}
```
- **Mục đích**: Báo cáo tổng kết và hướng dẫn next steps
- **Nội dung**: Thống kê, phân tích, recommendations
- **Sử dụng**: Project management, quality assurance
- **Đặc điểm**: Executive summary cho stakeholders
- **Ai sử dụng**: Project managers, quality assurance team

### **🎯 Mục đích sử dụng từng file**

| File | Ai sử dụng | Khi nào sử dụng | Tại sao quan trọng |
|------|------------|-----------------|-------------------|
| `complete.json` | Developers | Debugging, reprocessing | Backup đầy đủ |
| `chunks_summary.csv` | Business users | Content review | Human-readable |
| `embedding_ready.json` | **US-003 Pipeline** | **Vector embedding** | **Input chính cho AI** |
| `search_index.json` | Search engine | Real-time search | Performance optimization |
| `processed_data.pkl` | Python scripts | Fast loading | Development efficiency |
| `processing_report.json` | Project managers | Status reporting | Executive summary |

### **🚀 Workflow tiếp theo**

1. **embedding_ready.json** → US-003 Vector Embedding
2. **search_index.json** → Search functionality  
3. **chunks_summary.csv** → Content quality review
4. **processing_report.json** → Stakeholder reporting

**File quan trọng nhất**: `embedding_ready.json` - đây là input chính cho US-003! 🎯

### **📊 View Processing Report**
```bash
# Quick stats from report
python3.8 -c "
import json
report = json.load(open('/opt/rag-copilot/output/AI-Starter-Kit_final_output/processing_report.json'))
summary = report['processing_summary']
print('=== PROCESSING REPORT ===')
print(f'Source: {summary[\"source_file\"]}')
print(f'Total chunks: {summary[\"total_chunks\"]}')
print(f'Total tokens: {summary[\"total_tokens\"]}')
print(f'Avg tokens/chunk: {summary[\"avg_tokens_per_chunk\"]}')
print(f'Content types: {report[\"content_analysis\"][\"content_type_distribution\"]}')
print(f'Next steps: {report[\"ready_for_embedding\"][\"next_steps\"]}')
"
```

### **🔍 Test Data Loading**
```bash
# Test all formats can be loaded correctly
python3.8 -c "
import json, pickle, pandas as pd

# Test JSON
with open('/opt/rag-copilot/output/AI-Starter-Kit_final_output/AI-Starter-Kit_complete.json') as f:
    json_data = json.load(f)
print(f'JSON: {len(json_data[\"enhanced_chunks\"])} chunks')

# Test embedding ready
with open('/opt/rag-copilot/output/AI-Starter-Kit_final_output/embedding_ready.json') as f:
    embed_data = json.load(f)
print(f'Embedding ready: {len(embed_data[\"documents\"])} documents')

# Test CSV
df = pd.read_csv('/opt/rag-copilot/output/AI-Starter-Kit_final_output/chunks_summary.csv')
print(f'CSV: {len(df)} rows')

# Test pickle
with open('/opt/rag-copilot/output/AI-Starter-Kit_final_output/processed_data.pkl', 'rb') as f:
    pickle_data = pickle.load(f)
print(f'Pickle: {len(pickle_data[\"enhanced_chunks\"])} chunks')

print('✅ All formats loaded successfully!')
"
```

### **🚀 Ready for US-003 Embedding**
```bash
# The key file for next phase
echo "embedding_ready.json is ready for:"
echo "1. Vector embedding with sentence-transformers"
echo "2. Import to Chroma vector database"
echo "3. FAISS index creation"
echo "4. Retrieval testing"

# Check the file
ls -lh /opt/rag-copilot/output/AI-Starter-Kit_final_output/embedding_ready.json
```

---

## 🔍 **Tìm file MD của bạn**

### **Commands để tìm file**
```bash
# Tìm tất cả file .md trong hệ thống
find /home -name "*.md" 2>/dev/null | head -10
find /opt -name "*.md" 2>/dev/null | head -10
find /root -name "*.md" 2>/dev/null | head -10

# Tìm file cụ thể
find / -name "AI-Starter-Kit.md" 2>/dev/null
find / -name "*starter*" 2>/dev/null

# Kiểm tra file tồn tại
ls -la /path/to/your/document.md

# Kiểm tra nội dung file
head -20 /path/to/your/document.md
```

### **Test Pipeline với file của bạn**
```bash
# Thay thế /path/to/your/document.md bằng đường dẫn thực tế
python3.8 /opt/rag-copilot/scripts/test_pipeline.py /path/to/your/document.md

# Ví dụ các đường dẫn phổ biến:
python3.8 /opt/rag-copilot/scripts/test_pipeline.py /home/user/documents/AI-Starter-Kit.md
python3.8 /opt/rag-copilot/scripts/test_pipeline.py /root/documents/AI-Starter-Kit.md
python3.8 /opt/rag-copilot/scripts/test_pipeline.py /tmp/AI-Starter-Kit.md

# Kiểm tra log sau khi chạy
cat /opt/rag-copilot/logs/pipeline_test_*.log
```

### **Nếu không có file MD nào**
```bash
# Tạo file MD mẫu để test
cat > /tmp/test-document.md << 'EOF'
# Test Document

## Introduction
This is a test document for the RAG pipeline.

## Features
- Document processing
- Text chunking
- Metadata extraction

## Conclusion
This document will be processed by the pipeline.
EOF

# Test với file mẫu
python3.8 /opt/rag-copilot/scripts/test_pipeline.py /tmp/test-document.md
```

---

## 📝 **Notes**

- Always use `python3.8` instead of `python3` for the pipeline
- Output files are saved in `/opt/rag-copilot/output/`
- **`embedding_ready.json` is the most important file for US-003**
- **Thay thế đường dẫn file MD bằng đường dẫn thực tế của bạn**
- Backup important results before reprocessing
- Use UTF-8 encoding for all text files
- Check file sizes before processing very large documents
- The `_final_output` directory contains production-ready data

---

**For more help, check the main checklist:** `docs/deployment/us-002-processing-checklist.md` 