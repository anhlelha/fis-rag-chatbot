# 🚀 US-001 Deployment Guide: Local LLM Setup

## 📋 Overview

This guide provides step-by-step instructions for deploying Ollama with Mistral model on CentOS 8 server for Epic 1 - US-001: Local LLM Setup.

---

## 🎯 Objective

Set up Ollama with local LLM so that we can process queries without external API calls, supporting both Vietnamese and English queries.

---

## 📊 Prerequisites

### Server Requirements:
- **OS**: CentOS 8 or Rocky Linux 8
- **CPU**: 4+ cores \(Intel i5/Ryzen 5 or better\)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 30GB SSD for models and data
- **Network**: Internal network access only

### Access Requirements:
- SSH access to target server
- Sudo privileges on target server
- Server IP address, username, and password/SSH key

---

## 🔧 Deployment Options

### Option 1: Remote Deployment \(Recommended\)

Use the automated remote deployment script to install Ollama on your CentOS 8 server.

#### Step 1: Prepare Local Environment
```bash
# Navigate to scripts directory
cd scripts

# Make scripts executable
chmod +x setup_ollama_centos8.sh
chmod +x remote_deploy.sh

# Install sshpass if using password authentication
sudo apt-get update
sudo apt-get install sshpass
```

#### Step 2: Configure Server Connection
```bash
# Run configuration setup
./remote_deploy.sh config

# You'll be prompted for:
# - Server IP address
# - Server username
# - Authentication method (SSH key or password)
# - SSH key path or password
```

#### Step 3: Execute Remote Deployment
```bash
# Run full deployment
./remote_deploy.sh

# The script will:
# ✅ Validate configuration
# ✅ Test SSH connection
# ✅ Copy setup script to remote server
# ✅ Execute installation on remote server
# ✅ Verify installation
```

#### Step 4: Verify Installation
```bash
# Verify installation remotely
./remote_deploy.sh verify
```

### Option 2: Manual Server-Side Installation

If you prefer to install directly on the server:

#### Step 1: Copy Setup Script
```bash
# Copy setup script to server
scp scripts/setup_ollama_centos8.sh user@server:/tmp/
```

#### Step 2: Execute on Server
```bash
# SSH to server
ssh user@server

# Make script executable and run
chmod +x /tmp/setup_ollama_centos8.sh
sudo /tmp/setup_ollama_centos8.sh
```

---

## 📋 Installation Process

The setup script performs the following steps:

### 1. System Requirements Check
```bash
# Checks performed:
- OS version \(CentOS 8/Rocky Linux 8\)
- Memory \(minimum 8GB\)
- Disk space \(minimum 20GB\)
- CPU cores \(minimum 2\)
```

### 2. System Update
```bash
# Updates system and installs dependencies:
- curl, wget, unzip
- htop, net-tools
- firewalld, systemd
```

### 3. Ollama User Creation
```bash
# Creates dedicated ollama user:
- System user: /opt/ollama
- No shell access
- Proper permissions
```

### 4. Ollama Installation
```bash
# Downloads and installs Ollama:
- Official installation script
- Binary placed in /usr/local/bin/ollama
- Version verification
```

### 5. Systemd Service Configuration
```bash
# Creates systemd service:
- Service file: /etc/systemd/system/ollama.service
- Auto-start on boot
- Restart on failure
- Environment variables configured
```

### 6. Firewall Configuration
```bash
# Configures firewall:
- Opens port 11434/tcp
- Enables firewalld service
- Persistent configuration
```

### 7. Model Download and Testing
```bash
# Downloads Mistral model:
- Model: mistral:7b
- Vietnamese language test
- English language test
- Response verification
```

### 8. Health Check Script
```bash
# Creates health check script:
- Location: /usr/local/bin/ollama_health_check.sh
- Service status check
- API response check
- Model availability check
```

---

## ✅ Verification Steps

### 1. Service Status Check
```bash
# On server:
sudo systemctl status ollama

# Expected output:
# ● ollama.service - Ollama Service
#    Loaded: loaded (/etc/systemd/system/ollama.service; enabled; vendor preset: disabled)
#    Active: active (running) since ...
```

### 2. API Endpoint Test
```bash
# Test API endpoint:
curl -s http://localhost:11434/api/tags

# Expected output: JSON with model information
```

### 3. Model Response Test
```bash
# Test Vietnamese query:
ollama run mistral:7b "Xin chào, bạn có thể trả lời câu hỏi bằng tiếng Việt không?"

# Test English query:
ollama run mistral:7b "Hello, can you answer questions in English?"
```

### 4. Health Check
```bash
# Run health check:
/usr/local/bin/ollama_health_check.sh

# Expected output:
# ✅ Ollama is healthy
#    - Service: Running
#    - API: Responding
#    - Model: mistral:7b available
#    - Response time: <30 seconds
```

---

## 🔧 Post-Installation Configuration

### 1. Memory Optimization
```bash
# Edit service file if needed:
sudo systemctl edit ollama

# Add memory limits:
[Service]
Environment="OLLAMA_NUM_PARALLEL=2"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
```

### 2. Log Monitoring
```bash
# View logs:
sudo journalctl -u ollama -f

# Log rotation setup:
sudo journalctl --vacuum-time=7d
```

### 3. Performance Tuning
```bash
# Check resource usage:
htop

# Monitor model performance:
curl -s http://localhost:11434/api/ps
```

---

## 🚨 Troubleshooting

### Common Issues:

#### 1. Service Won't Start
```bash
# Check service status:
sudo systemctl status ollama

# Check logs:
sudo journalctl -u ollama --no-pager

# Common fixes:
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

#### 2. Model Download Issues
```bash
# Check disk space:
df -h

# Retry model download:
ollama pull mistral:7b

# Clear cache if needed:
ollama rm mistral:7b
ollama pull mistral:7b
```

#### 3. API Not Responding
```bash
# Check port binding:
netstat -tulpn | grep 11434

# Check firewall:
sudo firewall-cmd --list-ports

# Restart service:
sudo systemctl restart ollama
```

#### 4. Memory Issues
```bash
# Check memory usage:
free -h

# Kill and restart if needed:
sudo systemctl stop ollama
sudo systemctl start ollama
```

---

## 📊 Success Criteria Checklist

### US-001 Acceptance Criteria:
- [ ] Ollama installed and running on local server
- [ ] Mistral model downloaded and functional
- [ ] LLM responds to basic prompts in Vietnamese and English
- [ ] System uses only local compute resources
- [ ] No network calls to external LLM services

### Definition of Done:
- [ ] Ollama service running on port 11434
- [ ] Model responds to test queries within 10 seconds
- [ ] Documentation for setup process created
- [ ] Health check script implemented

---

## 🔄 Next Steps

After successful completion of US-001:

1. **Update Project Status**: Mark US-001 as complete
2. **Document Configuration**: Save server details for team reference
3. **Performance Baseline**: Record initial performance metrics
4. **Team Notification**: Inform team that LLM is ready for integration
5. **Begin US-002**: Start Document Processing Pipeline development

---

## 📞 Support Commands

### Server Management:
```bash
# Service management:
sudo systemctl start|stop|restart|status ollama

# View logs:
sudo journalctl -u ollama -f

# Check health:
/usr/local/bin/ollama_health_check.sh

# Test model:
ollama run mistral:7b "Test query"
```

### Model Management:
```bash
# List models:
ollama list

# Pull new model:
ollama pull model_name

# Remove model:
ollama rm model_name

# Show model info:
ollama show mistral:7b
```

### System Monitoring:
```bash
# Resource usage:
htop

# Port status:
netstat -tulpn | grep 11434

# Firewall status:
sudo firewall-cmd --list-ports

# Service status:
sudo systemctl status ollama
```

---

## 📋 Configuration Files

### Service Configuration:
```bash
# Service file location:
/etc/systemd/system/ollama.service

# Edit service:
sudo systemctl edit ollama
```

### Environment Variables:
```bash
# Key environment variables:
OLLAMA_HOST=0.0.0.0:11434
OLLAMA_ORIGINS=*
OLLAMA_NUM_PARALLEL=2
OLLAMA_MAX_LOADED_MODELS=1
```

---

**Epic 1 - US-001 Status**: Ready for Implementation  
**Dependencies**: CentOS 8 server with SSH access  
**Estimated Time**: 30-60 minutes  
**Next Story**: US-002 Document Processing Pipeline 