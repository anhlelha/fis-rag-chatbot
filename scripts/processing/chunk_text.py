#!/usr/bin/env python3.8
"""
Script chia text thành chunks cho RAG Pipeline
Đọc file JSON đã xử lý, chia thành chunks 500-1000 tokens
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict

def estimate_tokens(text: str) -> int:
    """Ước tính số tokens (xấp xỉ 1 token = 4 chars cho tiếng Việt)"""
    return len(text) // 4

def clean_text_advanced(text: str) -> str:
    """Làm sạch text nâng cao"""
    # Loại bỏ multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Loại bỏ empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)
    
    # Loại bỏ ký tự đặc biệt không cần thiết
    text = re.sub(r'[^\w\s\.,!?;:()\[\]"\'-]', ' ', text)
    
    return text.strip()

def chunk_by_sentences(text: str, max_tokens: int = 800, min_tokens: int = 400) -> List[str]:
    """Chia text theo câu, đảm bảo chunks có kích thước phù hợp"""
    # Tách câu
    sentences = re.split(r'[.!?]+\s+', text)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_tokens = estimate_tokens(sentence)
        
        # Nếu câu quá dài, chia nhỏ hơn
        if sentence_tokens > max_tokens:
            # Lưu chunk hiện tại nếu có
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # Chia câu dài thành từng phần
            words = sentence.split()
            temp_chunk = []
            temp_tokens = 0
            
            for word in words:
                word_tokens = estimate_tokens(word)
                if temp_tokens + word_tokens > max_tokens and temp_chunk:
                    chunks.append(' '.join(temp_chunk))
                    temp_chunk = [word]
                    temp_tokens = word_tokens
                else:
                    temp_chunk.append(word)
                    temp_tokens += word_tokens
            
            if temp_chunk:
                chunks.append(' '.join(temp_chunk))
                
        # Nếu thêm câu này vượt quá max_tokens
        elif current_tokens + sentence_tokens > max_tokens:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
    
    # Thêm chunk cuối cùng
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    # Gộp chunks quá nhỏ
    final_chunks = []
    i = 0
    while i < len(chunks):
        chunk = chunks[i]
        chunk_tokens = estimate_tokens(chunk)
        
        # Nếu chunk nhỏ hơn min_tokens, thử gộp với chunk tiếp theo
        if chunk_tokens < min_tokens and i + 1 < len(chunks):
            next_chunk = chunks[i + 1]
            combined_tokens = chunk_tokens + estimate_tokens(next_chunk)
            
            if combined_tokens <= max_tokens:
                final_chunks.append(chunk + ' ' + next_chunk)
                i += 2  # Skip next chunk
            else:
                final_chunks.append(chunk)
                i += 1
        else:
            final_chunks.append(chunk)
            i += 1
    
    return final_chunks

def chunk_by_headings(text: str, headings: List, max_tokens: int = 800) -> List[Dict]:
    """Chia text theo headings, giữ nguyên cấu trúc"""
    chunks_with_context = []
    
    if not headings:
        # Nếu không có headings, chia theo câu thông thường
        chunks = chunk_by_sentences(text, max_tokens)
        for i, chunk in enumerate(chunks):
            chunks_with_context.append({
                'chunk_id': i + 1,
                'content': chunk,
                'tokens': estimate_tokens(chunk),
                'context': 'general_content',
                'heading_level': 0,
                'heading_title': None
            })
        return chunks_with_context
    
    # Tìm vị trí của các headings trong text
    heading_positions = []
    for level, title in headings:
        # Tìm heading trong text
        pattern = re.escape(title)
        match = re.search(pattern, text)
        if match:
            heading_positions.append((match.start(), level, title))
    
    # Sắp xếp theo vị trí
    heading_positions.sort()
    
    # Chia text theo sections
    sections = []
    for i, (pos, level, title) in enumerate(heading_positions):
        start_pos = pos
        end_pos = heading_positions[i + 1][0] if i + 1 < len(heading_positions) else len(text)
        
        section_text = text[start_pos:end_pos].strip()
        if section_text:
            sections.append((level, title, section_text))
    
    # Tạo chunks từ các sections
    chunk_id = 1
    for level, title, section_text in sections:
        section_chunks = chunk_by_sentences(section_text, max_tokens)
        
        for chunk in section_chunks:
            chunks_with_context.append({
                'chunk_id': chunk_id,
                'content': chunk,
                'tokens': estimate_tokens(chunk),
                'context': f'section_{level}',
                'heading_level': level,
                'heading_title': title
            })
            chunk_id += 1
    
    return chunks_with_context

def process_chunks(input_file: str, output_file: str = None):
    """Xử lý chunking cho file JSON đã processed"""
    print(f"Đang xử lý chunking: {input_file}")
    
    try:
        # Đọc file JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data['clean_content']
        headings = data['metadata']['headings']
        
        print(f"📄 Text gốc: {estimate_tokens(text)} tokens")
        
        # Làm sạch text thêm
        clean_text = clean_text_advanced(text)
        print(f"🧹 Text đã làm sạch: {estimate_tokens(clean_text)} tokens")
        
        # Chunking theo headings
        chunks = chunk_by_headings(clean_text, headings)
        
        # Thống kê
        stats = {
            'total_chunks': len(chunks),
            'total_tokens': sum(chunk['tokens'] for chunk in chunks),
            'avg_tokens_per_chunk': sum(chunk['tokens'] for chunk in chunks) // len(chunks) if chunks else 0,
            'min_tokens': min(chunk['tokens'] for chunk in chunks) if chunks else 0,
            'max_tokens': max(chunk['tokens'] for chunk in chunks) if chunks else 0,
            'processed_time': datetime.now().isoformat()
        }
        
        # Tạo kết quả
        result = {
            'source_file': input_file,
            'original_metadata': data['metadata'],
            'chunks': chunks,
            'stats': stats
        }
        
        # Lưu kết quả
        if not output_file:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"/opt/rag-copilot/output/{base_name}_chunked.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Chunking hoàn thành!")
        print(f"📊 Thống kê:")
        print(f"   - Tổng chunks: {stats['total_chunks']}")
        print(f"   - Trung bình: {stats['avg_tokens_per_chunk']} tokens/chunk")
        print(f"   - Min: {stats['min_tokens']} tokens")
        print(f"   - Max: {stats['max_tokens']} tokens")
        print(f"💾 Đã lưu: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Lỗi xử lý chunking: {e}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python3.8 chunk_text.py <processed_file.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"File không tồn tại: {input_file}")
        sys.exit(1)
    
    if not input_file.lower().endswith('.json'):
        print(f"File không phải định dạng JSON: {input_file}")
        sys.exit(1)
    
    process_chunks(input_file)

if __name__ == "__main__":
    main() 