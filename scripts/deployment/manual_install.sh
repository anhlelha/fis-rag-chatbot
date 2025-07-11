#!/bin/bash

# Manual installation script
ssh -i ../private_key root@10.14.190.5 << 'EOF'
echo "=== Manual Ollama Installation ==="
echo "Date: $(date)"
echo ""

cd /tmp
if [ -f "setup_ollama_centos8.sh" ]; then
    echo "✅ Setup script found"
    chmod +x setup_ollama_centos8.sh
    echo "▶️ Running installation script..."
    ./setup_ollama_centos8.sh 2>&1 | tee ollama_install.log
else
    echo "❌ Setup script not found"
fi
EOF 