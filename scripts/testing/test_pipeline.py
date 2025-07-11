#!/usr/bin/env python3.8
"""
Script kiểm thử toàn bộ pipeline xử lý tài liệu
Chạy end-to-end test và tạo log báo cáo
"""

import json
import sys
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

def log_message(message, log_file):
    """Ghi log message với timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def run_command(command, log_file, description):
    """Chạy command và log kết quả"""
    log_message(f"🔄 {description}", log_file)
    log_message(f"Command: {command}", log_file)
    
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        
        duration = round(end_time - start_time, 2)
        
        if result.returncode == 0:
            log_message(f"✅ SUCCESS ({duration}s): {description}", log_file)
            if result.stdout.strip():
                log_message(f"Output: {result.stdout.strip()}", log_file)
            return True, result.stdout
        else:
            log_message(f"❌ FAILED ({duration}s): {description}", log_file)
            log_message(f"Error: {result.stderr.strip()}", log_file)
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        log_message(f"⏰ TIMEOUT (300s): {description}", log_file)
        return False, "Command timed out"
    except Exception as e:
        log_message(f"💥 EXCEPTION: {description} - {str(e)}", log_file)
        return False, str(e)

def check_file_exists(file_path, log_file, description):
    """Kiểm tra file tồn tại"""
    if Path(file_path).exists():
        file_size = Path(file_path).stat().st_size
        log_message(f"✅ FILE EXISTS: {description} - {file_path} ({file_size} bytes)", log_file)
        return True
    else:
        log_message(f"❌ FILE MISSING: {description} - {file_path}", log_file)
        return False

def validate_json_file(file_path, log_file, expected_structure=None):
    """Validate JSON file structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if expected_structure:
            for key in expected_structure:
                if key not in data:
                    log_message(f"❌ JSON VALIDATION: Missing key '{key}' in {file_path}", log_file)
                    return False
        
        log_message(f"✅ JSON VALID: {file_path}", log_file)
        return True, data
        
    except Exception as e:
        log_message(f"❌ JSON INVALID: {file_path} - {str(e)}", log_file)
        return False, None

def test_full_pipeline(input_md_file, base_dir="/opt/rag-copilot"):
    """Test toàn bộ pipeline từ MD file đến final output"""
    
    # Setup
    log_file = Path(base_dir) / "logs" / f"pipeline_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file.parent.mkdir(exist_ok=True)
    
    log_message("=" * 60, log_file)
    log_message("🚀 STARTING FULL PIPELINE TEST", log_file)
    log_message("=" * 60, log_file)
    log_message(f"Input file: {input_md_file}", log_file)
    log_message(f"Base directory: {base_dir}", log_file)
    log_message(f"Log file: {log_file}", log_file)
    
    # Test results tracking
    test_results = {
        'start_time': datetime.now().isoformat(),
        'input_file': input_md_file,
        'steps': {},
        'files_created': [],
        'errors': [],
        'overall_success': False
    }
    
    try:
        # Step 1: Process MD file
        log_message("\n📄 STEP 1: Processing MD file", log_file)
        cmd1 = f"python3.8 {base_dir}/scripts/processing/process_md.py {input_md_file}"
        success1, output1 = run_command(cmd1, log_file, "Process MD file")
        test_results['steps']['step1_process_md'] = success1
        
        if not success1:
            test_results['errors'].append("Step 1 failed: MD processing")
            return test_results
        
        # Check processed file
        file_name = Path(input_md_file).stem
        processed_file = f"{base_dir}/output/{file_name}_processed.json"
        if not check_file_exists(processed_file, log_file, "Processed MD file"):
            test_results['errors'].append("Processed file not created")
            return test_results
        test_results['files_created'].append(processed_file)
        
        # Validate processed JSON
        valid, processed_data = validate_json_file(processed_file, log_file, 
                                                 ['metadata', 'clean_content', 'stats'])
        if not valid:
            test_results['errors'].append("Invalid processed JSON")
            return test_results
        
        # Step 2: Chunking
        log_message("\n✂️ STEP 2: Text chunking", log_file)
        cmd2 = f"python3.8 {base_dir}/scripts/processing/simple_chunk.py {processed_file}"
        success2, output2 = run_command(cmd2, log_file, "Text chunking")
        test_results['steps']['step2_chunking'] = success2
        
        if not success2:
            test_results['errors'].append("Step 2 failed: Chunking")
            return test_results
        
        # Check chunked file
        chunked_file = f"{base_dir}/output/{file_name}_simple_chunked.json"
        if not check_file_exists(chunked_file, log_file, "Chunked file"):
            test_results['errors'].append("Chunked file not created")
            return test_results
        test_results['files_created'].append(chunked_file)
        
        # Validate chunked JSON
        valid, chunked_data = validate_json_file(chunked_file, log_file, 
                                                ['chunks', 'stats', 'original_metadata'])
        if not valid:
            test_results['errors'].append("Invalid chunked JSON")
            return test_results
        
        # Step 3: Metadata extraction
        log_message("\n🏷️ STEP 3: Metadata extraction", log_file)
        cmd3 = f"python3.8 {base_dir}/scripts/processing/extract_metadata.py {chunked_file}"
        success3, output3 = run_command(cmd3, log_file, "Metadata extraction")
        test_results['steps']['step3_metadata'] = success3
        
        if not success3:
            test_results['errors'].append("Step 3 failed: Metadata extraction")
            return test_results
        
        # Check metadata file
        metadata_file = f"{base_dir}/output/{file_name}_with_metadata.json"
        if not check_file_exists(metadata_file, log_file, "Metadata file"):
            test_results['errors'].append("Metadata file not created")
            return test_results
        test_results['files_created'].append(metadata_file)
        
        # Validate metadata JSON
        valid, metadata_data = validate_json_file(metadata_file, log_file, 
                                                 ['enhanced_chunks', 'metadata_stats'])
        if not valid:
            test_results['errors'].append("Invalid metadata JSON")
            return test_results
        
        # Step 4: Data storage
        log_message("\n💾 STEP 4: Data storage", log_file)
        cmd4 = f"python3.8 {base_dir}/scripts/processing/save_processed_data.py {metadata_file}"
        success4, output4 = run_command(cmd4, log_file, "Data storage")
        test_results['steps']['step4_storage'] = success4
        
        if not success4:
            test_results['errors'].append("Step 4 failed: Data storage")
            return test_results
        
        # Check final output directory
        final_dir = f"{base_dir}/output/{file_name}_final_output"
        if not Path(final_dir).exists():
            test_results['errors'].append("Final output directory not created")
            return test_results
        
        # Check all expected files in final output
        expected_files = [
            f"{file_name}_complete.json",
            "chunks_summary.csv",
            "embedding_ready.json",
            "search_index.json",
            "processed_data.pkl",
            "processing_report.json"
        ]
        
        for expected_file in expected_files:
            file_path = Path(final_dir) / expected_file
            if check_file_exists(file_path, log_file, f"Final output: {expected_file}"):
                test_results['files_created'].append(str(file_path))
            else:
                test_results['errors'].append(f"Missing final output: {expected_file}")
        
        # Step 5: Quality check (prepare embedding)
        log_message("\n🔍 STEP 5: Quality check (prepare embedding)", log_file)
        cmd5 = f"python3.8 {base_dir}/scripts/testing/prepare_embedding.py {final_dir}"
        success5, output5 = run_command(cmd5, log_file, "Quality check and embedding preparation")
        test_results['steps']['step5_quality_check'] = success5
        
        if not success5:
            test_results['errors'].append("Step 5 failed: Quality check")
            return test_results
        
        # Check quality check outputs
        embedding_config_file = Path(final_dir) / "embedding_config.json"
        preparation_report_file = Path(final_dir) / "embedding_preparation_report.json"
        
        if check_file_exists(embedding_config_file, log_file, "Embedding config"):
            test_results['files_created'].append(str(embedding_config_file))
        else:
            test_results['errors'].append("Missing embedding_config.json")
        
        if check_file_exists(preparation_report_file, log_file, "Preparation report"):
            test_results['files_created'].append(str(preparation_report_file))
        else:
            test_results['errors'].append("Missing embedding_preparation_report.json")
        
        # Step 6: Final validation
        log_message("\n🧪 STEP 6: Final validation", log_file)
        
        # Test embedding_ready.json
        embedding_file = Path(final_dir) / "embedding_ready.json"
        valid, embed_data = validate_json_file(embedding_file, log_file, 
                                              ['documents', 'metadata', 'ids'])
        if valid:
            log_message(f"✅ Embedding ready: {len(embed_data['documents'])} documents", log_file)
            test_results['steps']['step6_validation'] = True
        else:
            test_results['errors'].append("Invalid embedding_ready.json")
            return test_results
        
        # Validate preparation report
        if preparation_report_file.exists():
            valid_report, report_data = validate_json_file(preparation_report_file, log_file,
                                                         ['validation_results', 'ready_for_us003'])
            if valid_report and report_data.get('ready_for_us003'):
                log_message("✅ Quality check passed: Ready for US-003", log_file)
            else:
                test_results['errors'].append("Quality check failed: Not ready for US-003")
                return test_results
        
        # Test CSV loading
        csv_file = Path(final_dir) / "chunks_summary.csv"
        cmd_csv = f"python3.8 -c \"import pandas as pd; df = pd.read_csv('{csv_file}'); print(f'CSV loaded: {{len(df)}} rows')\""
        success_csv, output_csv = run_command(cmd_csv, log_file, "CSV validation")
        
        # Test pickle loading
        pickle_file = Path(final_dir) / "processed_data.pkl"
        cmd_pickle = f"python3.8 -c \"import pickle; data = pickle.load(open('{pickle_file}', 'rb')); print(f'Pickle loaded: {{len(data[\\\"enhanced_chunks\\\"])}} chunks')\""
        success_pickle, output_pickle = run_command(cmd_pickle, log_file, "Pickle validation")
        
        # Final statistics
        log_message("\n📊 PIPELINE STATISTICS", log_file)
        log_message(f"Original file: {Path(input_md_file).name}", log_file)
        log_message(f"File size: {Path(input_md_file).stat().st_size} bytes", log_file)
        log_message(f"Chunks created: {len(embed_data['documents'])}", log_file)
        log_message(f"Files created: {len(test_results['files_created'])}", log_file)
        
        # Success!
        test_results['overall_success'] = True
        log_message("\n🎉 PIPELINE TEST COMPLETED SUCCESSFULLY!", log_file)
        
    except Exception as e:
        log_message(f"\n💥 PIPELINE TEST FAILED: {str(e)}", log_file)
        test_results['errors'].append(f"Pipeline exception: {str(e)}")
    
    finally:
        test_results['end_time'] = datetime.now().isoformat()
        test_results['duration'] = (datetime.fromisoformat(test_results['end_time']) - 
                                   datetime.fromisoformat(test_results['start_time'])).total_seconds()
        
        # Save test results
        results_file = Path(base_dir) / "logs" / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        log_message(f"\n📋 Test results saved: {results_file}", log_file)
        log_message("=" * 60, log_file)
        
        return test_results

def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python3.8 test_pipeline.py <input_md_file>")
        print("Ví dụ: python3.8 test_pipeline.py /path/to/document.md")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not Path(input_file).exists():
        print(f"❌ File không tồn tại: {input_file}")
        sys.exit(1)
    
    if not input_file.lower().endswith('.md'):
        print(f"❌ File không phải định dạng .md: {input_file}")
        sys.exit(1)
    
    print("🚀 Starting full pipeline test...")
    print(f"📄 Input file: {input_file}")
    
    # Run test
    results = test_full_pipeline(input_file)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Overall success: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
    print(f"Duration: {results['duration']:.2f} seconds")
    print(f"Files created: {len(results['files_created'])}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\n❌ ERRORS:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['overall_success']:
        print("\n🎉 Pipeline test completed successfully!")
        print("✅ Quality check passed - Ready for US-003 embedding phase")
    else:
        print("\n💥 Pipeline test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 