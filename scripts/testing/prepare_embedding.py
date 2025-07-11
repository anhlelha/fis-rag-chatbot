#!/usr/bin/env python3.8
"""
Script chuẩn bị dữ liệu cho embedding phase (US-003)
Kiểm tra và validate format dữ liệu đầu ra từ pipeline
"""

import json
import sys
import os
import pickle
from pathlib import Path
from datetime import datetime

def validate_embedding_ready_format(file_path):
    """Validate format của embedding_ready.json"""
    print(f"🔍 Validating embedding_ready format: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Kiểm tra structure bắt buộc
        required_keys = ['documents', 'metadata', 'ids']
        for key in required_keys:
            if key not in data:
                print(f"❌ Missing required key: {key}")
                return False
        
        # Kiểm tra documents
        documents = data['documents']
        if not isinstance(documents, list):
            print("❌ 'documents' must be a list")
            return False
        
        if len(documents) == 0:
            print("❌ 'documents' list is empty")
            return False
        
        # Kiểm tra metadata
        metadata = data['metadata']
        if not isinstance(metadata, list):
            print("❌ 'metadata' must be a list")
            return False
        
        if len(metadata) != len(documents):
            print(f"❌ Metadata length ({len(metadata)}) != documents length ({len(documents)})")
            return False
        
        # Kiểm tra ids
        ids = data['ids']
        if not isinstance(ids, list):
            print("❌ 'ids' must be a list")
            return False
        
        if len(ids) != len(documents):
            print(f"❌ IDs length ({len(ids)}) != documents length ({len(documents)})")
            return False
        
        # Kiểm tra unique IDs
        if len(set(ids)) != len(ids):
            print("❌ IDs are not unique")
            return False
        
        # Kiểm tra content của documents
        for i, doc in enumerate(documents):
            if not isinstance(doc, str):
                print(f"❌ Document {i} is not a string")
                return False
            
            if len(doc.strip()) == 0:
                print(f"❌ Document {i} is empty")
                return False
        
        # Kiểm tra metadata structure
        for i, meta in enumerate(metadata):
            if not isinstance(meta, dict):
                print(f"❌ Metadata {i} is not a dict")
                return False
            
            # Kiểm tra required metadata fields
            required_meta_fields = ['chunk_id', 'source_file', 'type']
            for field in required_meta_fields:
                if field not in meta:
                    print(f"❌ Metadata {i} missing required field: {field}")
                    return False
        
        print(f"✅ Embedding ready format is valid")
        print(f"   - Documents: {len(documents)}")
        print(f"   - Metadata: {len(metadata)}")
        print(f"   - IDs: {len(ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating embedding_ready.json: {str(e)}")
        return False

def check_encoding_utf8(file_path):
    """Kiểm tra encoding UTF-8"""
    print(f"🔍 Checking UTF-8 encoding: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ File is properly UTF-8 encoded ({len(content)} characters)")
        return True
        
    except UnicodeDecodeError as e:
        print(f"❌ UTF-8 encoding error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error checking encoding: {str(e)}")
        return False

def analyze_text_content(embedding_ready_file):
    """Phân tích nội dung text cho embedding"""
    print(f"📊 Analyzing text content for embedding...")
    
    try:
        with open(embedding_ready_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = data['documents']
        metadata = data['metadata']
        
        # Thống kê cơ bản
        total_chars = sum(len(doc) for doc in documents)
        total_words = sum(len(doc.split()) for doc in documents)
        avg_chars_per_doc = total_chars / len(documents)
        avg_words_per_doc = total_words / len(documents)
        
        print(f"📈 Text Statistics:")
        print(f"   - Total documents: {len(documents)}")
        print(f"   - Total characters: {total_chars:,}")
        print(f"   - Total words: {total_words:,}")
        print(f"   - Average chars per document: {avg_chars_per_doc:.1f}")
        print(f"   - Average words per document: {avg_words_per_doc:.1f}")
        
        # Phân tích content types
        content_types = {}
        for meta in metadata:
            content_type = meta.get('type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        print(f"📋 Content Types:")
        for content_type, count in content_types.items():
            print(f"   - {content_type}: {count} documents")
        
        # Kiểm tra text quality
        quality_issues = []
        
        for i, doc in enumerate(documents):
            # Kiểm tra quá ngắn
            if len(doc.strip()) < 50:
                quality_issues.append(f"Document {i} too short ({len(doc)} chars)")
            
            # Kiểm tra quá dài
            if len(doc) > 10000:
                quality_issues.append(f"Document {i} too long ({len(doc)} chars)")
            
            # Kiểm tra special characters (relaxed line break check)
            if doc.count('\n') > 50:  # Increased from 20 to 50 for more lenient checking
                quality_issues.append(f"Document {i} has too many line breaks")
        
        if quality_issues:
            print(f"⚠️ Quality Issues Found:")
            for issue in quality_issues[:5]:  # Show first 5 issues
                print(f"   - {issue}")
            if len(quality_issues) > 5:
                print(f"   ... and {len(quality_issues) - 5} more issues")
        else:
            print("✅ No quality issues found")
        
        return {
            'total_documents': len(documents),
            'total_characters': total_chars,
            'total_words': total_words,
            'avg_chars_per_doc': avg_chars_per_doc,
            'avg_words_per_doc': avg_words_per_doc,
            'content_types': content_types,
            'quality_issues': quality_issues
        }
        
    except Exception as e:
        print(f"❌ Error analyzing text content: {str(e)}")
        return None

def create_embedding_config(output_dir):
    """Tạo config file cho embedding phase"""
    print(f"⚙️ Creating embedding configuration...")
    
    config = {
        "embedding_config": {
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "dimension": 384,
            "batch_size": 32,
            "max_length": 512
        },
        "vector_store_config": {
            "type": "chromadb",
            "collection_name": "fis_internal_docs",
            "persist_directory": "/opt/rag-copilot/vector_store"
        },
        "processing_config": {
            "chunk_overlap": 0,
            "normalize_embeddings": True,
            "remove_duplicates": True
        },
        "created_at": datetime.now().isoformat(),
        "ready_for_us003": True
    }
    
    config_file = Path(output_dir) / "embedding_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Embedding config saved: {config_file}")
    return config_file

def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python3.8 prepare_embedding.py <final_output_directory>")
        print("Ví dụ: python3.8 prepare_embedding.py /opt/rag-copilot/output/AI-Starter-Kit_final_output")
        sys.exit(1)
    
    final_output_dir = sys.argv[1]
    
    if not Path(final_output_dir).exists():
        print(f"❌ Directory không tồn tại: {final_output_dir}")
        sys.exit(1)
    
    print("🚀 PREPARING DATA FOR EMBEDDING PHASE (US-003)")
    print("=" * 60)
    print(f"Final output directory: {final_output_dir}")
    
    # Test files
    embedding_ready_file = Path(final_output_dir) / "embedding_ready.json"
    
    if not embedding_ready_file.exists():
        print(f"❌ embedding_ready.json not found: {embedding_ready_file}")
        sys.exit(1)
    
    # Validation steps
    results = {}
    
    # Step 1: Validate format
    results['format_valid'] = validate_embedding_ready_format(embedding_ready_file)
    
    # Step 2: Check encoding
    results['encoding_valid'] = check_encoding_utf8(embedding_ready_file)
    
    # Step 3: Analyze content
    analysis = analyze_text_content(embedding_ready_file)
    results['content_analysis'] = analysis is not None
    
    # Step 4: Create config
    if all(results.values()):
        config_file = create_embedding_config(final_output_dir)
        results['config_created'] = config_file.exists()
    else:
        results['config_created'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 EMBEDDING PREPARATION SUMMARY")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    overall_success = all(results.values())
    print(f"\nOverall: {'✅ READY FOR US-003' if overall_success else '❌ NOT READY'}")
    
    if overall_success:
        print("\n🎉 Data is ready for embedding phase!")
        print("✅ Next steps:")
        print("   1. Run US-003 embedding pipeline")
        print("   2. Use embedding_ready.json as input")
        print("   3. Follow embedding_config.json settings")
        
        # Save preparation report
        report = {
            "timestamp": datetime.now().isoformat(),
            "final_output_dir": final_output_dir,
            "validation_results": results,
            "content_analysis": analysis,
            "ready_for_us003": overall_success
        }
        
        report_file = Path(final_output_dir) / "embedding_preparation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"   4. Check preparation report: {report_file}")
        
    else:
        print("\n💥 Fix the failed validations before proceeding to US-003")
        sys.exit(1)

if __name__ == "__main__":
    main() 