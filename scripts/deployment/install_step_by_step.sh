#!/bin/bash

echo "=== Step-by-Step Ollama Installation ==="

echo "Step 1: Creating ollama user..."
ssh -i ../private_key root@10.14.190.5 "useradd -r -s /bin/false -d /opt/ollama ollama"

echo "Step 2: Installing Ollama..."
ssh -i ../private_key root@10.14.190.5 "curl -fsSL https://ollama.com/install.sh | sh"

echo "Step 3: Creating systemd service..."
ssh -i ../private_key root@10.14.190.5 "cat > /etc/systemd/system/ollama.service << 'EOL'
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ollama
Group=ollama
WorkingDirectory=/opt/ollama
ExecStart=/usr/local/bin/ollama serve
Environment=OLLAMA_HOST=0.0.0.0:11434
Environment=OLLAMA_ORIGINS=*
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL"

echo "Step 4: Starting service..."
ssh -i ../private_key root@10.14.190.5 "systemctl daemon-reload && systemctl enable ollama && systemctl start ollama"

echo "Step 5: Configuring firewall..."
ssh -i ../private_key root@10.14.190.5 "firewall-cmd --permanent --add-port=11434/tcp && firewall-cmd --reload"

echo "Step 6: Downloading Mistral model..."
ssh -i ../private_key root@10.14.190.5 "sleep 10 && ollama pull mistral:7b"

echo "Step 7: Testing..."
ssh -i ../private_key root@10.14.190.5 "ollama run mistral:7b 'Hello'" 