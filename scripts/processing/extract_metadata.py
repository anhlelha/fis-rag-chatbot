#!/usr/bin/env python3.8
"""
Script trích xuất metadata nâng cao cho RAG Pipeline
Gắn metadata chi tiết vào từng chunk
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path

def extract_chunk_metadata(chunk, chunk_index, original_metadata, total_chunks):
    """Trích xuất metadata cho một chunk"""
    
    content = chunk['content']
    
    # Phân loại nội dung chunk
    content_type = classify_content_type(content)
    
    # Tính toán vị trí trong document
    position_ratio = (chunk_index + 1) / total_chunks
    
    # Trích xuất keywords quan trọng
    keywords = extract_keywords(content)
    
    # Phân tích structure
    structure_info = analyze_structure(content)
    
    # Metadata nâng cao
    metadata = {
        # Thông tin cơ bản
        'chunk_id': chunk['chunk_id'],
        'source_file': original_metadata['file_name'],
        'source_path': original_metadata['file_path'],
        'source_title': original_metadata['title'],
        
        # Thông tin vị trí
        'position_in_doc': {
            'index': chunk_index,
            'total_chunks': total_chunks,
            'ratio': round(position_ratio, 3),
            'section': get_document_section(position_ratio)
        },
        
        # Thông tin nội dung
        'content_info': {
            'type': content_type,
            'tokens': chunk['tokens'],
            'words': chunk['words'],
            'chars': chunk['chars'],
            'sentences': count_sentences(content),
            'keywords': keywords,
            'language': detect_language(content)
        },
        
        # Thông tin cấu trúc
        'structure': structure_info,
        
        # Metadata gốc
        'source_metadata': {
            'created_time': original_metadata['created_time'],
            'modified_time': original_metadata['modified_time'],
            'file_size': original_metadata['file_size']
        },
        
        # Metadata xử lý
        'processing_metadata': {
            'processed_time': datetime.now().isoformat(),
            'processor_version': '1.0.0',
            'chunk_method': 'simple_sentence_based'
        }
    }
    
    return metadata

def classify_content_type(content):
    """Phân loại loại nội dung của chunk"""
    content_lower = content.lower()
    
    # Kiểm tra các pattern
    if any(word in content_lower for word in ['hướng dẫn', 'cài đặt', 'setup', 'install']):
        return 'instruction'
    elif any(word in content_lower for word in ['tổng quan', 'giới thiệu', 'overview', 'introduction']):
        return 'overview'
    elif any(word in content_lower for word in ['công cụ', 'tool', 'phần mềm', 'software']):
        return 'tool_description'
    elif any(word in content_lower for word in ['ví dụ', 'example', 'demo', 'mẫu']):
        return 'example'
    elif any(word in content_lower for word in ['khuyến nghị', 'recommend', 'nên', 'should']):
        return 'recommendation'
    elif content.count('```') >= 2 or content.count('`') >= 4:
        return 'code_example'
    elif content.count('http') > 0 or content.count('www') > 0:
        return 'reference_with_links'
    else:
        return 'general_content'

def extract_keywords(content, max_keywords=10):
    """Trích xuất keywords quan trọng từ content"""
    
    # Loại bỏ stop words tiếng Việt và tiếng Anh
    stop_words = {
        'và', 'hoặc', 'nhưng', 'vì', 'nên', 'để', 'từ', 'trong', 'trên', 'dưới', 'với', 'của', 'cho', 'về',
        'the', 'and', 'or', 'but', 'for', 'with', 'from', 'to', 'in', 'on', 'at', 'by', 'as', 'is', 'are',
        'this', 'that', 'these', 'those', 'a', 'an'
    }
    
    # Tách từ và làm sạch
    words = re.findall(r'\w+', content.lower())
    
    # Lọc từ có ý nghĩa (độ dài >= 3, không phải stop word)
    meaningful_words = [
        word for word in words 
        if len(word) >= 3 and word not in stop_words
    ]
    
    # Đếm tần suất
    word_freq = {}
    for word in meaningful_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sắp xếp theo tần suất và lấy top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
    
    return [{'word': word, 'frequency': freq} for word, freq in keywords]

def analyze_structure(content):
    """Phân tích cấu trúc của chunk"""
    
    # Đếm các elements
    bullet_points = len(re.findall(r'^[\s]*[-*+]\s', content, re.MULTILINE))
    numbered_lists = len(re.findall(r'^[\s]*\d+\.\s', content, re.MULTILINE))
    code_blocks = content.count('```')
    inline_code = content.count('`') - code_blocks * 6  # Trừ đi code blocks
    links = len(re.findall(r'http[s]?://[^\s]+', content))
    emphasis = content.count('**') + content.count('*')
    
    return {
        'has_bullet_points': bullet_points > 0,
        'bullet_points_count': bullet_points,
        'has_numbered_lists': numbered_lists > 0,
        'numbered_lists_count': numbered_lists,
        'has_code_blocks': code_blocks > 0,
        'code_blocks_count': code_blocks // 2,  # Mỗi code block có 2 ```
        'has_inline_code': inline_code > 0,
        'inline_code_count': max(0, inline_code // 2),
        'has_links': links > 0,
        'links_count': links,
        'has_emphasis': emphasis > 0,
        'emphasis_count': emphasis // 2,
        'structure_complexity': calculate_structure_complexity(bullet_points, numbered_lists, code_blocks, links)
    }

def calculate_structure_complexity(bullets, numbers, code, links):
    """Tính độ phức tạp cấu trúc (0-5)"""
    complexity = 0
    
    if bullets > 0: complexity += 1
    if numbers > 0: complexity += 1
    if code > 0: complexity += 1
    if links > 0: complexity += 1
    if bullets + numbers > 5: complexity += 1  # Nhiều lists
    
    return min(complexity, 5)

def count_sentences(content):
    """Đếm số câu trong content"""
    sentences = re.split(r'[.!?]+', content)
    return len([s for s in sentences if s.strip()])

def detect_language(content):
    """Phát hiện ngôn ngữ chính (đơn giản)"""
    vietnamese_chars = len(re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', content.lower()))
    english_chars = len(re.findall(r'[a-z]', content.lower()))
    
    if vietnamese_chars > english_chars * 0.1:
        return 'vietnamese'
    else:
        return 'english'

def get_document_section(position_ratio):
    """Xác định phần của tài liệu (beginning, middle, end)"""
    if position_ratio <= 0.3:
        return 'beginning'
    elif position_ratio <= 0.7:
        return 'middle'
    else:
        return 'end'

def process_metadata_extraction(input_file):
    """Xử lý trích xuất metadata cho file chunked"""
    
    print(f"Đang trích xuất metadata: {input_file}")
    
    try:
        # Đọc file chunked
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data['chunks']
        original_metadata = data['original_metadata']
        original_stats = data['stats']
        
        print(f"Xử lý {len(chunks)} chunks từ {original_metadata['file_name']}")
        
        # Trích xuất metadata cho từng chunk
        enhanced_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = extract_chunk_metadata(chunk, i, original_metadata, len(chunks))
            
            enhanced_chunk = {
                'chunk_id': chunk['chunk_id'],
                'content': chunk['content'],
                'basic_stats': {
                    'tokens': chunk['tokens'],
                    'words': chunk['words'],
                    'chars': chunk['chars']
                },
                'metadata': chunk_metadata
            }
            enhanced_chunks.append(enhanced_chunk)
        
        # Thống kê metadata
        content_types = {}
        languages = {}
        total_keywords = 0
        
        for chunk in enhanced_chunks:
            content_type = chunk['metadata']['content_info']['type']
            language = chunk['metadata']['content_info']['language']
            keywords_count = len(chunk['metadata']['content_info']['keywords'])
            
            content_types[content_type] = content_types.get(content_type, 0) + 1
            languages[language] = languages.get(language, 0) + 1
            total_keywords += keywords_count
        
        metadata_stats = {
            'content_type_distribution': content_types,
            'language_distribution': languages,
            'avg_keywords_per_chunk': total_keywords // len(chunks) if chunks else 0,
            'metadata_extraction_time': datetime.now().isoformat()
        }
        
        # Tạo kết quả
        result = {
            'source_file': input_file,
            'original_metadata': original_metadata,
            'original_stats': original_stats,
            'enhanced_chunks': enhanced_chunks,
            'metadata_stats': metadata_stats,
            'processing_info': {
                'processor': 'metadata_extractor_v1.0',
                'processed_time': datetime.now().isoformat(),
                'total_chunks_processed': len(enhanced_chunks)
            }
        }
        
        # Lưu file
        output_file = input_file.replace('_simple_chunked.json', '_with_metadata.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # In kết quả
        print(f"\n✅ Metadata extraction hoàn thành!")
        print(f"📊 Thống kê metadata:")
        print(f"   - Content types: {dict(content_types)}")
        print(f"   - Languages: {dict(languages)}")
        print(f"   - Avg keywords/chunk: {metadata_stats['avg_keywords_per_chunk']}")
        
        print(f"\n📖 Preview chunk đầu tiên:")
        first_chunk = enhanced_chunks[0]
        print(f"   - Type: {first_chunk['metadata']['content_info']['type']}")
        print(f"   - Keywords: {[kw['word'] for kw in first_chunk['metadata']['content_info']['keywords'][:5]]}")
        print(f"   - Structure: {first_chunk['metadata']['structure']['structure_complexity']}/5 complexity")
        
        print(f"\n💾 Đã lưu: {output_file}")
        return result
        
    except Exception as e:
        print(f"❌ Lỗi metadata extraction: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python3.8 extract_metadata.py <chunked_file.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not Path(input_file).exists():
        print(f"File không tồn tại: {input_file}")
        sys.exit(1)
    
    if not input_file.endswith('_chunked.json'):
        print(f"File không phải định dạng chunked JSON: {input_file}")
        sys.exit(1)
    
    process_metadata_extraction(input_file)

if __name__ == "__main__":
    main() 