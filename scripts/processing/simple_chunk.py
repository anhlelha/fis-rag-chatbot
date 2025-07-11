#!/usr/bin/env python3.8
"""
Script chunking đơn giản cho RAG Pipeline
Chia text theo câu, không phụ thuộc vào headings
"""

import json
import re
import sys
from datetime import datetime

def simple_chunk_text(text, max_tokens=800, min_tokens=200):
    """Chia text thành chunks theo câu"""
    
    # Tách câu
    sentences = re.split(r'[.!?]+\s+', text)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Ước tính tokens (1 token ≈ 4 chars cho tiếng Việt)
        sentence_tokens = len(sentence) // 4
        
        # Nếu câu quá dài, chia nhỏ hơn
        if sentence_tokens > max_tokens:
            # Lưu chunk hiện tại
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            # Chia câu dài thành các phần
            words = sentence.split()
            temp_chunk = []
            temp_tokens = 0
            
            for word in words:
                word_tokens = len(word) // 4
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
    
    # Thêm chunk cuối
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    # Gộp chunks quá nhỏ với chunk tiếp theo
    final_chunks = []
    i = 0
    while i < len(chunks):
        chunk = chunks[i]
        chunk_tokens = len(chunk) // 4
        
        if chunk_tokens < min_tokens and i + 1 < len(chunks):
            next_chunk = chunks[i + 1]
            combined_tokens = chunk_tokens + len(next_chunk) // 4
            
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

def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python3.8 simple_chunk.py <processed_file.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Đọc file processed
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data['clean_content']
        original_metadata = data['metadata']
        
        print(f"Đang xử lý file: {original_metadata['file_name']}")
        print(f"Text length: {len(text)} chars")
        print(f"Estimated tokens: {len(text) // 4}")
        
        # Chunking
        chunks_text = simple_chunk_text(text)
        
        # Tạo chunks với metadata
        chunks = []
        for i, chunk_content in enumerate(chunks_text):
            chunk_tokens = len(chunk_content) // 4
            chunks.append({
                'chunk_id': i + 1,
                'content': chunk_content,
                'tokens': chunk_tokens,
                'chars': len(chunk_content),
                'words': len(chunk_content.split())
            })
        
        # Thống kê
        total_tokens = sum(chunk['tokens'] for chunk in chunks)
        avg_tokens = total_tokens // len(chunks) if chunks else 0
        min_tokens = min(chunk['tokens'] for chunk in chunks) if chunks else 0
        max_tokens = max(chunk['tokens'] for chunk in chunks) if chunks else 0
        
        stats = {
            'total_chunks': len(chunks),
            'total_tokens': total_tokens,
            'avg_tokens_per_chunk': avg_tokens,
            'min_tokens': min_tokens,
            'max_tokens': max_tokens,
            'processed_time': datetime.now().isoformat()
        }
        
        # Tạo kết quả
        result = {
            'source_file': input_file,
            'original_metadata': original_metadata,
            'chunks': chunks,
            'stats': stats
        }
        
        # Lưu file
        output_file = input_file.replace('_processed.json', '_simple_chunked.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # In kết quả
        print(f"\n✅ Chunking hoàn thành!")
        print(f"📊 Thống kê:")
        print(f"   - Tổng chunks: {stats['total_chunks']}")
        print(f"   - Trung bình: {stats['avg_tokens_per_chunk']} tokens/chunk")
        print(f"   - Min: {stats['min_tokens']} tokens")
        print(f"   - Max: {stats['max_tokens']} tokens")
        print(f"   - Tổng tokens: {stats['total_tokens']}")
        
        print(f"\n📖 Preview 3 chunks đầu:")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i+1} ({chunk['tokens']} tokens):")
            preview = chunk['content'][:150]
            print(f"{preview}{'...' if len(chunk['content']) > 150 else ''}")
        
        print(f"\n💾 Đã lưu: {output_file}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 