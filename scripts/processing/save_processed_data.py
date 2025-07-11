#!/usr/bin/env python3.8
"""
Script lưu trữ và tổ chức dữ liệu đã xử lý cho RAG Pipeline
Tạo các format khác nhau để sử dụng cho embedding và retrieval
"""

import json
import csv
import sys
import pickle
from datetime import datetime
from pathlib import Path
import pandas as pd
import re

def create_csv_export(enhanced_chunks, output_dir):
    """Tạo file CSV cho dễ dàng xem và phân tích"""
    
    csv_data = []
    for chunk in enhanced_chunks:
        metadata = chunk['metadata']
        
        row = {
            'chunk_id': chunk['chunk_id'],
            'content': chunk['content'][:500] + '...' if len(chunk['content']) > 500 else chunk['content'],
            'tokens': chunk['basic_stats']['tokens'],
            'words': chunk['basic_stats']['words'],
            'chars': chunk['basic_stats']['chars'],
            'content_type': metadata['content_info']['type'],
            'language': metadata['content_info']['language'],
            'section': metadata['position_in_doc']['section'],
            'position_ratio': metadata['position_in_doc']['ratio'],
            'keywords': ', '.join([kw['word'] for kw in metadata['content_info']['keywords'][:5]]),
            'structure_complexity': metadata['structure']['structure_complexity'],
            'has_code': metadata['structure']['has_code_blocks'],
            'has_links': metadata['structure']['has_links'],
            'sentence_count': metadata['content_info']['sentences'],
            'source_file': metadata['source_file']
        }
        csv_data.append(row)
    
    # Lưu CSV
    csv_file = output_dir / 'chunks_summary.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if csv_data:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
    
    return csv_file

def create_embedding_ready_format(enhanced_chunks, output_dir):
    """Tạo format sẵn sàng cho embedding"""
    
    embedding_data = {
        'documents': [],
        'metadata': [],
        'ids': []
    }
    
    for chunk in enhanced_chunks:
        # Clean content - remove excessive line breaks
        cleaned_content = clean_text_for_embedding(chunk['content'])
        
        # Document text for embedding
        embedding_data['documents'].append(cleaned_content)
        
        # Compact metadata for vector store
        compact_metadata = {
            'chunk_id': chunk['chunk_id'],
            'source_file': chunk['metadata']['source_file'],  # Fixed: use source_file instead of source
            'type': chunk['metadata']['content_info']['type'],
            'section': chunk['metadata']['position_in_doc']['section'],
            'tokens': chunk['basic_stats']['tokens'],
            'keywords': [kw['word'] for kw in chunk['metadata']['content_info']['keywords'][:3]],
            'language': chunk['metadata']['content_info']['language']
        }
        embedding_data['metadata'].append(compact_metadata)
        
        # Unique ID for each chunk
        chunk_id = f"{chunk['metadata']['source_file']}_{chunk['chunk_id']}"
        embedding_data['ids'].append(chunk_id)
    
    # Lưu JSON format cho embedding
    embedding_file = output_dir / 'embedding_ready.json'
    with open(embedding_file, 'w', encoding='utf-8') as f:
        json.dump(embedding_data, f, ensure_ascii=False, indent=2)
    
    return embedding_file

def clean_text_for_embedding(text):
    """Clean text để tối ưu cho embedding"""
    
    # Remove excessive line breaks (more than 2 consecutive)
    
    # Replace multiple consecutive line breaks with double line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple consecutive spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove trailing/leading whitespace from each line
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines]
    
    # Join back but avoid empty lines at start/end
    text = '\n'.join(cleaned_lines).strip()
    
    # Remove more than 2 consecutive empty lines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    return text

def create_search_index(enhanced_chunks, output_dir):
    """Tạo search index đơn giản"""
    
    search_index = {
        'documents': {},
        'keyword_index': {},
        'type_index': {},
        'section_index': {}
    }
    
    for chunk in enhanced_chunks:
        chunk_id = str(chunk['chunk_id'])
        metadata = chunk['metadata']
        
        # Document store
        search_index['documents'][chunk_id] = {
            'content': chunk['content'],
            'metadata': metadata['content_info'],
            'stats': chunk['basic_stats']
        }
        
        # Keyword index
        for kw in metadata['content_info']['keywords']:
            word = kw['word']
            if word not in search_index['keyword_index']:
                search_index['keyword_index'][word] = []
            search_index['keyword_index'][word].append(chunk_id)
        
        # Type index
        content_type = metadata['content_info']['type']
        if content_type not in search_index['type_index']:
            search_index['type_index'][content_type] = []
        search_index['type_index'][content_type].append(chunk_id)
        
        # Section index
        section = metadata['position_in_doc']['section']
        if section not in search_index['section_index']:
            search_index['section_index'][section] = []
        search_index['section_index'][section].append(chunk_id)
    
    # Lưu search index
    index_file = output_dir / 'search_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    
    return index_file

def create_pickle_backup(data, output_dir):
    """Tạo backup dạng pickle cho load nhanh"""
    
    pickle_file = output_dir / 'processed_data.pkl'
    with open(pickle_file, 'wb') as f:
        pickle.dump(data, f)
    
    return pickle_file

def create_summary_report(data, output_files, output_dir):
    """Tạo summary report"""
    
    enhanced_chunks = data['enhanced_chunks']
    metadata_stats = data['metadata_stats']
    
    # Tính toán thống kê
    total_chunks = len(enhanced_chunks)
    total_tokens = sum(chunk['basic_stats']['tokens'] for chunk in enhanced_chunks)
    total_words = sum(chunk['basic_stats']['words'] for chunk in enhanced_chunks)
    
    # Phân tích content types
    type_distribution = metadata_stats['content_type_distribution']
    
    # Phân tích keywords phổ biến
    all_keywords = {}
    for chunk in enhanced_chunks:
        for kw in chunk['metadata']['content_info']['keywords']:
            word = kw['word']
            freq = kw['frequency']
            all_keywords[word] = all_keywords.get(word, 0) + freq
    
    top_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # Tạo report
    report = {
        'processing_summary': {
            'source_file': data['original_metadata']['file_name'],
            'processed_time': datetime.now().isoformat(),
            'total_chunks': total_chunks,
            'total_tokens': total_tokens,
            'total_words': total_words,
            'avg_tokens_per_chunk': total_tokens // total_chunks if total_chunks > 0 else 0,
            'avg_words_per_chunk': total_words // total_chunks if total_chunks > 0 else 0
        },
        
        'content_analysis': {
            'content_type_distribution': type_distribution,
            'language_distribution': metadata_stats['language_distribution'],
            'top_keywords': [{'word': word, 'total_frequency': freq} for word, freq in top_keywords]
        },
        
        'chunk_details': [
            {
                'chunk_id': chunk['chunk_id'],
                'tokens': chunk['basic_stats']['tokens'],
                'type': chunk['metadata']['content_info']['type'],
                'section': chunk['metadata']['position_in_doc']['section'],
                'keywords_count': len(chunk['metadata']['content_info']['keywords']),
                'structure_complexity': chunk['metadata']['structure']['structure_complexity'],
                'preview': chunk['content'][:100] + '...' if len(chunk['content']) > 100 else chunk['content']
            }
            for chunk in enhanced_chunks
        ],
        
        'output_files': {
            'main_data': str(output_files['main']),
            'csv_summary': str(output_files['csv']),
            'embedding_ready': str(output_files['embedding']),
            'search_index': str(output_files['search']),
            'pickle_backup': str(output_files['pickle'])
        },
        
        'ready_for_embedding': {
            'status': 'ready',
            'recommendation': 'Dữ liệu đã sẵn sàng cho bước embedding với vector store',
            'next_steps': [
                'Sử dụng embedding_ready.json cho vector embedding',
                'Import vào vector database (Chroma/FAISS)',
                'Test retrieval với search_index.json'
            ]
        }
    }
    
    # Lưu report
    report_file = output_dir / 'processing_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_file, report

def load_and_validate_data(input_file):
    """Load và validate dữ liệu từ file với metadata"""
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate structure
        required_keys = ['enhanced_chunks', 'metadata_stats', 'original_metadata']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        print(f"✅ Validated data structure: {len(data['enhanced_chunks'])} chunks")
        return data
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

def process_data_storage(input_file):
    """Main function xử lý lưu trữ dữ liệu"""
    
    print(f"Đang xử lý lưu trữ dữ liệu: {input_file}")
    
    # Load data
    data = load_and_validate_data(input_file)
    if not data:
        return None
    
    # Tạo output directory
    input_path = Path(input_file)
    base_name = input_path.stem.replace('_with_metadata', '')
    output_dir = input_path.parent / f"{base_name}_final_output"
    output_dir.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    
    # Copy main data file
    main_file = output_dir / f"{base_name}_complete.json"
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Tạo các format khác nhau
    print("📊 Tạo CSV summary...")
    csv_file = create_csv_export(data['enhanced_chunks'], output_dir)
    
    print("🔮 Tạo embedding-ready format...")
    embedding_file = create_embedding_ready_format(data['enhanced_chunks'], output_dir)
    
    print("🔍 Tạo search index...")
    search_file = create_search_index(data['enhanced_chunks'], output_dir)
    
    print("💾 Tạo pickle backup...")
    pickle_file = create_pickle_backup(data, output_dir)
    
    # Tạo summary report
    output_files = {
        'main': main_file,
        'csv': csv_file,
        'embedding': embedding_file,
        'search': search_file,
        'pickle': pickle_file
    }
    
    print("📋 Tạo summary report...")
    report_file, report = create_summary_report(data, output_files, output_dir)
    
    # In kết quả
    print(f"\n✅ Lưu trữ dữ liệu hoàn thành!")
    print(f"📂 Output directory: {output_dir}")
    print(f"📄 Files created:")
    for name, path in output_files.items():
        file_size = Path(path).stat().st_size // 1024  # KB
        print(f"   - {name}: {Path(path).name} ({file_size} KB)")
    
    print(f"\n📊 Summary:")
    summary = report['processing_summary']
    print(f"   - Total chunks: {summary['total_chunks']}")
    print(f"   - Total tokens: {summary['total_tokens']}")
    print(f"   - Avg tokens/chunk: {summary['avg_tokens_per_chunk']}")
    
    print(f"\n🚀 Ready for next steps:")
    for step in report['ready_for_embedding']['next_steps']:
        print(f"   - {step}")
    
    return output_dir

def test_data_loading(output_dir):
    """Test load lại dữ liệu để đảm bảo integrity"""
    
    print(f"\n🧪 Testing data loading from {output_dir}...")
    
    try:
        # Test JSON load
        main_file = output_dir / "AI-Starter-Kit_complete.json"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            print(f"✅ JSON load: {len(json_data['enhanced_chunks'])} chunks")
        
        # Test pickle load
        pickle_file = output_dir / "processed_data.pkl"
        if pickle_file.exists():
            with open(pickle_file, 'rb') as f:
                pickle_data = pickle.load(f)
            print(f"✅ Pickle load: {len(pickle_data['enhanced_chunks'])} chunks")
        
        # Test CSV load
        csv_file = output_dir / "chunks_summary.csv"
        if csv_file.exists():
            df = pd.read_csv(csv_file)
            print(f"✅ CSV load: {len(df)} rows")
        
        print("✅ All data formats load successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python3.8 save_processed_data.py <metadata_file.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not Path(input_file).exists():
        print(f"File không tồn tại: {input_file}")
        sys.exit(1)
    
    if not input_file.endswith('_with_metadata.json'):
        print(f"File không phải định dạng metadata JSON: {input_file}")
        sys.exit(1)
    
    # Process data storage
    output_dir = process_data_storage(input_file)
    
    if output_dir:
        # Test data loading
        test_data_loading(output_dir)
        print(f"\n💾 Dữ liệu đã được lưu trữ và validate thành công!")
        print(f"📁 Location: {output_dir}")

if __name__ == "__main__":
    main() 