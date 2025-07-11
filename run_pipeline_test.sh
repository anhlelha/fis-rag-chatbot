#!/bin/bash

# RAG Pipeline Test Runner
# Wrapper script to avoid line ending issues

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path_to_md_file>"
    echo "Example: $0 /u01/anhlh/RGA/AIFirst/pilot_projects/AI-Starter-Kit.md"
    exit 1
fi

MD_FILE="$1"
SCRIPT_DIR="/opt/rag-copilot/scripts"

echo "🚀 RAG Pipeline Test Runner"
echo "=========================="
echo "MD File: $MD_FILE"
echo "Script Dir: $SCRIPT_DIR"

# Check if file exists
if [ ! -f "$MD_FILE" ]; then
    echo "❌ Error: File not found: $MD_FILE"
    exit 1
fi

# Check if Python 3.8 is available
if ! command -v python3.8 &> /dev/null; then
    echo "❌ Error: python3.8 not found"
    exit 1
fi

# Check if script exists
if [ ! -f "$SCRIPT_DIR/test_pipeline.py" ]; then
    echo "❌ Error: test_pipeline.py not found in $SCRIPT_DIR"
    exit 1
fi

echo "✅ All checks passed. Running pipeline test..."
echo ""

# Run the pipeline test directly with Python
python3.8 "$SCRIPT_DIR/test_pipeline.py" "$MD_FILE"

echo ""
echo "📋 Check results:"
echo "   Log files: ls -la /opt/rag-copilot/logs/"
echo "   Output: ls -la /opt/rag-copilot/output/" 