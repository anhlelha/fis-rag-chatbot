#!/usr/bin/env python3.8
"""
Script tìm file MD trên server để sử dụng với pipeline
"""

import os
import sys
from pathlib import Path

def find_md_files(search_paths=None):
    """Tìm tất cả file .md trong các đường dẫn phổ biến"""
    
    if search_paths is None:
        search_paths = [
            '/home',
            '/opt', 
            '/root',
            '/tmp',
            '/var',
            '/usr/local'
        ]
    
    found_files = []
    
    print("🔍 Đang tìm file .md...")
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        print(f"   Tìm trong {search_path}...")
        
        try:
            for root, dirs, files in os.walk(search_path):
                # Skip hidden directories and system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['proc', 'sys', 'dev']]
                
                for file in files:
                    if file.lower().endswith('.md'):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            found_files.append({
                                'path': file_path,
                                'name': file,
                                'size': file_size,
                                'size_kb': file_size // 1024
                            })
                        except (OSError, PermissionError):
                            continue
                            
        except PermissionError:
            print(f"   ⚠️ Không có quyền truy cập {search_path}")
            continue
    
    return found_files

def display_results(found_files):
    """Hiển thị kết quả tìm kiếm"""
    
    if not found_files:
        print("❌ Không tìm thấy file .md nào")
        return
    
    print(f"\n✅ Tìm thấy {len(found_files)} file .md:")
    print("-" * 80)
    
    # Sort by size (descending)
    found_files.sort(key=lambda x: x['size'], reverse=True)
    
    for i, file_info in enumerate(found_files, 1):
        print(f"{i:2d}. {file_info['name']}")
        print(f"    Path: {file_info['path']}")
        print(f"    Size: {file_info['size_kb']} KB")
        
        # Show first few lines of file
        try:
            with open(file_info['path'], 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line:
                    preview = first_line[:60] + "..." if len(first_line) > 60 else first_line
                    print(f"    Preview: {preview}")
        except:
            print(f"    Preview: (không thể đọc)")
        
        print()

def generate_test_commands(found_files):
    """Tạo commands để test pipeline"""
    
    if not found_files:
        return
    
    print("🚀 Commands để test pipeline:")
    print("-" * 50)
    
    for i, file_info in enumerate(found_files[:5], 1):  # Show top 5
        print(f"# Test với file {i}: {file_info['name']}")
        print(f"python3.8 /opt/rag-copilot/scripts/test_pipeline.py {file_info['path']}")
        print()

def create_sample_md():
    """Tạo file MD mẫu nếu không tìm thấy file nào"""
    
    sample_content = """# Sample Document for RAG Pipeline

## Introduction
This is a sample document created for testing the RAG (Retrieval-Augmented Generation) pipeline.

## Features
The RAG pipeline includes the following components:
- Document processing and cleaning
- Text chunking with optimal size
- Metadata extraction and enhancement
- Multiple output formats for different use cases

## Technical Details
### Processing Steps
1. **Document Parsing**: Extract text and basic metadata
2. **Text Cleaning**: Remove markdown syntax and normalize content
3. **Chunking**: Split text into manageable pieces (200-800 tokens)
4. **Metadata Enhancement**: Add content classification and keywords
5. **Output Generation**: Create multiple formats for downstream use

### Output Formats
- Complete JSON with full metadata
- Embedding-ready format for vector databases
- CSV summary for human analysis
- Search index for fast retrieval
- Pickle backup for Python applications
- Processing report with statistics

## Use Cases
This pipeline can be used for:
- Internal knowledge base processing
- Document search and retrieval
- AI-powered question answering
- Content analysis and categorization

## Conclusion
The RAG pipeline provides a robust foundation for processing internal documents and preparing them for AI applications.
"""
    
    sample_file = "/tmp/sample-rag-document.md"
    
    try:
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"✅ Đã tạo file mẫu: {sample_file}")
        print(f"📄 Kích thước: {len(sample_content)} characters")
        print(f"🚀 Test command:")
        print(f"python3.8 /opt/rag-copilot/scripts/test_pipeline.py {sample_file}")
        
        return sample_file
        
    except Exception as e:
        print(f"❌ Lỗi tạo file mẫu: {e}")
        return None

def main():
    print("📋 MD File Finder for RAG Pipeline")
    print("=" * 50)
    
    # Custom search paths from command line
    search_paths = None
    if len(sys.argv) > 1:
        search_paths = sys.argv[1:]
        print(f"🔍 Tìm trong: {', '.join(search_paths)}")
    
    # Find MD files
    found_files = find_md_files(search_paths)
    
    # Display results
    display_results(found_files)
    
    # Generate test commands
    generate_test_commands(found_files)
    
    # Create sample if no files found
    if not found_files:
        print("\n💡 Tạo file mẫu để test pipeline...")
        sample_file = create_sample_md()
        
        if sample_file:
            found_files = [{'path': sample_file, 'name': 'sample-rag-document.md', 'size': 0}]
            generate_test_commands(found_files)

if __name__ == "__main__":
    main() 