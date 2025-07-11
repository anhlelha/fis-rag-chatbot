#!/usr/bin/env python3
"""
Script khắc phục lỗi embedding preparation
Chạy lại pipeline từ Step 6 với các fix đã được áp dụng
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Chạy command với error handling"""
    print(f"\n🔄 {description}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def main():
    print("🚀 FIXING EMBEDDING PREPARATION ERRORS")
    print("=" * 60)
    
    # Định nghĩa các file paths
    metadata_file = "/opt/rag-copilot/output/AI-Starter-Kit_with_metadata.json"
    
    print(f"📁 Working with metadata file: {metadata_file}")
    
    # Check if metadata file exists
    if not os.path.exists(metadata_file):
        print(f"❌ Metadata file not found: {metadata_file}")
        print("💡 Please run the pipeline from Step 5 first:")
        print("   python scripts/processing/extract_metadata.py /path/to/chunked_file.json")
        sys.exit(1)
    
    print("\n🔧 FIXES APPLIED:")
    print("✅ Fixed source_file field in embedding_ready format")
    print("✅ Added text cleaning to remove excessive line breaks")
    print("✅ Organized scripts into proper directory structure")
    
    # Step 6: Re-run save_processed_data.py with fixes
    step6_success = run_command(
        f"python scripts/processing/save_processed_data.py {metadata_file}",
        "Step 6: Save processed data (with fixes)"
    )
    
    if not step6_success:
        print("❌ Step 6 failed. Cannot proceed.")
        sys.exit(1)
    
    # Find the output directory
    output_dir = "/opt/rag-copilot/output/AI-Starter-Kit_final_output"
    
    # Step 7: Run prepare_embedding.py
    step7_success = run_command(
        f"python scripts/testing/prepare_embedding.py {output_dir}",
        "Step 7: Prepare embedding (validation)"
    )
    
    if step7_success:
        print("\n🎉 EMBEDDING PREPARATION FIXED!")
        print("✅ All validation checks should now pass")
        print("✅ Data is ready for US-003 (Vector Embedding)")
        
        print("\n📋 NEXT STEPS:")
        print("1. Verify the embedding_ready.json format is correct")
        print("2. Proceed with US-003 implementation")
        print("3. Import data into vector database (Chroma/FAISS)")
        
        print(f"\n📁 Output files location: {output_dir}")
        print("📄 Key files:")
        print("   - embedding_ready.json (for US-003)")
        print("   - complete.json (full backup)")
        print("   - chunks_summary.csv (human-readable)")
        print("   - processing_report.json (summary)")
        
    else:
        print("\n❌ EMBEDDING PREPARATION STILL HAS ISSUES")
        print("💡 Please check the error messages above and:")
        print("1. Verify all required fields are present")
        print("2. Check text cleaning is working properly")
        print("3. Ensure UTF-8 encoding is correct")

if __name__ == "__main__":
    main() 