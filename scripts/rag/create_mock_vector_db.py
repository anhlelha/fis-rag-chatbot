#!/usr/bin/env python3.8
"""
Create Mock Vector Database for Step 4 Testing
Generate minimal vector database files to test RAG pipeline
"""

import os
import sys
import json
import numpy as np
from datetime import datetime

def create_mock_vector_db():
    """Create mock vector database files"""
    print("🔧 Creating mock vector database for Step 4 testing...")
    
    # Create directories
    vector_db_dir = "/opt/rag-copilot/data/vector_db"
    data_dir = "/opt/rag-copilot/data"
    
    os.makedirs(vector_db_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"✅ Created directories: {vector_db_dir}")
    
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
        print("✅ Required libraries available")
    except ImportError as e:
        print(f"❌ Missing libraries: {e}")
        print("Install with: pip3.8 install faiss-cpu sentence-transformers")
        return False
    
    # Sample documents for testing
    sample_docs = [
        {
            "content": "Quy trình nghỉ phép của công ty FIS: Nhân viên cần nộp đơn xin nghỉ phép trước ít nhất 3 ngày làm việc. Đơn xin nghỉ phép phải được quản lý trực tiếp phê duyệt. Nhân viên có thể nghỉ phép tối đa 12 ngày/năm.",
            "source": "employee_handbook.md",
            "title": "Employee Handbook - Leave Policy",
            "section": "Leave Management"
        },
        {
            "content": "Expense reimbursement process: Employees must submit expense reports within 30 days of incurring the expense. All receipts must be attached. Manager approval is required for expenses over $100. Reimbursement will be processed within 5 business days.",
            "source": "finance_policy.md", 
            "title": "Finance Policy - Expense Reimbursement",
            "section": "Financial Procedures"
        },
        {
            "content": "Quy trình xin tăng lương: Nhân viên có thể đề xuất tăng lương trong cuộc đánh giá hiệu suất hàng năm. Cần có bằng chứng về thành tích và đóng góp. Quyết định tăng lương sẽ được HR và quản lý cấp cao xem xét.",
            "source": "hr_policy.md",
            "title": "HR Policy - Salary Review", 
            "section": "Compensation"
        },
        {
            "content": "Training and development policy: FIS Corporation provides professional development opportunities for all employees. Training budget is allocated annually. Employees can request training through their manager. External training requires advance approval.",
            "source": "training_policy.md",
            "title": "Training Policy - Professional Development",
            "section": "Employee Development"
        }
    ]
    
    print(f"📄 Creating mock documents: {len(sample_docs)} items")
    
    # Initialize embedding model
    print("🤖 Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    print("🔢 Generating embeddings...")
    contents = [doc["content"] for doc in sample_docs]
    embeddings = model.encode(contents)
    
    print(f"✅ Generated {len(embeddings)} embeddings, dimension: {embeddings.shape[1]}")
    
    # Create FAISS index
    print("🗂️  Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product similarity
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings.astype('float32'))
    
    # Save FAISS index
    faiss_path = os.path.join(vector_db_dir, "document_vectors.faiss")
    faiss.write_index(index, faiss_path)
    print(f"✅ FAISS index saved: {faiss_path}")
    
    # Create metadata
    print("📋 Creating metadata...")
    metadata = {}
    for i, doc in enumerate(sample_docs):
        metadata[str(i)] = {
            "content": doc["content"],
            "source": doc["source"],
            "title": doc["title"],
            "section": doc["section"],
            "document_id": i,
            "created_at": datetime.now().isoformat()
        }
    
    # Save metadata
    metadata_path = os.path.join(vector_db_dir, "document_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✅ Metadata saved: {metadata_path}")
    
    # Create processed documents file
    print("📄 Creating processed documents file...")
    processed_docs = {
        "documents": sample_docs,
        "total_documents": len(sample_docs),
        "processing_date": datetime.now().isoformat(),
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_dimension": dimension,
        "note": "Mock data for Step 4 testing"
    }
    
    processed_path = os.path.join(data_dir, "processed_documents.json")
    with open(processed_path, 'w', encoding='utf-8') as f:
        json.dump(processed_docs, f, ensure_ascii=False, indent=2)
    print(f"✅ Processed documents saved: {processed_path}")
    
    # Verify files
    print("\n🔍 Verifying created files...")
    files_to_check = [faiss_path, metadata_path, processed_path]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} - {size} bytes")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            return False
    
    print("\n🎉 Mock vector database created successfully!")
    print("📊 Summary:")
    print(f"  - Documents: {len(sample_docs)}")
    print(f"  - Embeddings: {len(embeddings)} x {dimension}D")
    print(f"  - FAISS index: {index.ntotal} vectors")
    print(f"  - Files created: {len(files_to_check)}")
    
    print("\n🚀 Ready for Step 4 testing!")
    print("Test with: python3.8 test_generate_response.py")
    
    return True

if __name__ == "__main__":
    success = create_mock_vector_db()
    sys.exit(0 if success else 1) 