#!/usr/bin/env python3.8
"""
Script xử lý file Markdown (.md) cho RAG Pipeline
Đọc file .md, trích xuất nội dung text và metadata
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path

def extract_metadata_from_md(file_path):
    """Trích xuất metadata từ file markdown"""
    metadata = {
        'file_name': os.path.basename(file_path),
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'created_time': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
        'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
        'title': None,
        'headings': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Tìm title (heading đầu tiên)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Tìm tất cả headings
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        metadata['headings'] = [(len(h[0]), h[1].strip()) for h in headings]
        
    except Exception as e:
        print(f"Lỗi đọc metadata từ {file_path}: {e}")
    
    return metadata

def process_markdown_file(file_path):
    """Xử lý một file markdown"""
    print(f"Đang xử lý: {file_path}")
    
    try:
        # Đọc nội dung file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trích xuất metadata
        metadata = extract_metadata_from_md(file_path)
        
        # Làm sạch nội dung (loại bỏ markdown syntax cơ bản)
        clean_content = clean_markdown_content(content)
        
        # Thống kê
        stats = {
            'total_chars': len(content),
            'clean_chars': len(clean_content),
            'lines': len(content.split('\n')),
            'words': len(clean_content.split()),
            'headings_count': len(metadata['headings'])
        }
        
        result = {
            'metadata': metadata,
            'content': content,
            'clean_content': clean_content,
            'stats': stats
        }
        
        print(f"✅ Xử lý thành công: {stats['words']} từ, {stats['headings_count']} headings")
        return result
        
    except Exception as e:
        print(f"❌ Lỗi xử lý {file_path}: {e}")
        return None

def clean_markdown_content(content):
    """Làm sạch nội dung markdown"""
    # Loại bỏ markdown syntax cơ bản
    clean = content
    
    # Loại bỏ headers markdown
    clean = re.sub(r'^#{1,6}\s+', '', clean, flags=re.MULTILINE)
    
    # Loại bỏ bold/italic
    clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)  # **bold**
    clean = re.sub(r'\*([^*]+)\*', r'\1', clean)      # *italic*
    clean = re.sub(r'__([^_]+)__', r'\1', clean)      # __bold__
    clean = re.sub(r'_([^_]+)_', r'\1', clean)        # _italic_
    
    # Loại bỏ links
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)  # [text](url)
    
    # Loại bỏ code blocks
    clean = re.sub(r'```[^`]*```', '', clean, flags=re.DOTALL)
    clean = re.sub(r'`([^`]+)`', r'\1', clean)  # inline code
    
    # Loại bỏ multiple spaces và newlines
    clean = re.sub(r'\n\s*\n', '\n\n', clean)
    clean = re.sub(r' +', ' ', clean)
    
    return clean.strip()

def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python3.8 process_md.py <file_path.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"File không tồn tại: {file_path}")
        sys.exit(1)
    
    if not file_path.lower().endswith('.md'):
        print(f"File không phải định dạng .md: {file_path}")
        sys.exit(1)
    
    # Xử lý file
    result = process_markdown_file(file_path)
    
    if result:
        # In thông tin metadata
        print("\n📋 METADATA:")
        print(f"Title: {result['metadata']['title']}")
        print(f"File: {result['metadata']['file_name']}")
        print(f"Size: {result['metadata']['file_size']} bytes")
        print(f"Words: {result['stats']['words']}")
        print(f"Headings: {result['stats']['headings_count']}")
        
        print("\n📖 CONTENT PREVIEW (first 300 chars):")
        preview = result['clean_content'][:300]
        print(f"{preview}{'...' if len(result['clean_content']) > 300 else ''}")
        
        # Lưu kết quả ra file JSON
        output_file = f"/opt/rag-copilot/output/{Path(file_path).stem}_processed.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Đã lưu kết quả: {output_file}")
    
if __name__ == "__main__":
    main() 