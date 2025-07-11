#!/bin/bash

# Simple server check script
ssh -i ../private_key root@10.14.190.5 << 'EOF'
echo "=== Server Status Check ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo ""

echo "=== Checking Ollama Installation ==="
if command -v ollama &> /dev/null; then
    echo "✅ Ollama command found"
    ollama --version
else
    echo "❌ Ollama command not found"
fi
echo ""

echo "=== Checking Ollama Service ==="
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama service is running"
    systemctl status ollama --no-pager
else
    echo "❌ Ollama service not running"
    echo "Service status:"
    systemctl status ollama --no-pager || echo "Service not found"
fi
echo ""

echo "=== Checking Port 11434 ==="
if netstat -tulpn | grep -q 11434; then
    echo "✅ Port 11434 is listening"
    netstat -tulpn | grep 11434
else
    echo "❌ Port 11434 not listening"
fi
echo ""

echo "=== Checking Processes ==="
ps aux | grep -v grep | grep ollama || echo "No ollama processes found"
echo ""

echo "=== Checking Installation Log ==="
if [ -f "/tmp/ollama_install.log" ]; then
    echo "Last 10 lines of install log:"
    tail -10 /tmp/ollama_install.log
fi
echo ""

echo "=== Checking System Resources ==="
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h
echo ""
EOF 