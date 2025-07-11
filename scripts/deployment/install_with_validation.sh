#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Progress tracking file
PROGRESS_FILE="./installation_progress.log"

# Function to update progress
update_progress() {
    local step="$1"
    local status="$2"
    local notes="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Create backup of progress file
    cp "$PROGRESS_FILE" "${PROGRESS_FILE}.bak" 2>/dev/null || true
    
    # Update the specific step
    if grep -q "^${step}|" "$PROGRESS_FILE"; then
        # Update existing step
        sed -i "s/^${step}|.*$/${step}|${status}|${timestamp}|${notes}/" "$PROGRESS_FILE"
    else
        # Add new step
        echo "${step}|${status}|${timestamp}|${notes}" >> "$PROGRESS_FILE"
    fi
    
    echo -e "${YELLOW}📝 Progress: ${step} -> ${status}${NC}"
}

# Function to run SSH command and check result
run_ssh_command() {
    local step_id="$1"
    local description="$2"
    local command="$3"
    local validation="$4"
    
    echo -e "${BLUE}=== $description ===${NC}"
    echo "Command: $command"
    
    # Mark step as in progress
    update_progress "$step_id" "IN_PROGRESS" "$description"
    
    # Run the command
    ssh -i ../private_key root@10.14.190.5 "$command"
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo -e "${RED}❌ Command failed with exit code: $exit_code${NC}"
        update_progress "$step_id" "FAILED" "Command failed with exit code: $exit_code"
        return 1
    fi
    
    # Run validation if provided
    if [ -n "$validation" ]; then
        echo "Validating: $validation"
        ssh -i ../private_key root@10.14.190.5 "$validation" > /dev/null 2>&1
        local val_code=$?
        
        if [ $val_code -eq 0 ]; then
            echo -e "${GREEN}✅ Step completed successfully${NC}"
            update_progress "$step_id" "COMPLETED" "Validation passed"
            echo ""
            return 0
        else
            echo -e "${RED}❌ Validation failed${NC}"
            update_progress "$step_id" "FAILED" "Validation failed"
            return 1
        fi
    else
        echo -e "${GREEN}✅ Step completed${NC}"
        update_progress "$step_id" "COMPLETED" "No validation required"
        echo ""
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name="$1"
    local max_wait="$2"
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready (max ${max_wait}s)...${NC}"
    
    for i in $(seq 1 $max_wait); do
        if ssh -i ../private_key root@10.14.190.5 "systemctl is-active --quiet $service_name"; then
            echo -e "${GREEN}✅ $service_name is ready${NC}"
            return 0
        fi
        echo "  Waiting... ($i/${max_wait}s)"
        sleep 1
    done
    
    echo -e "${RED}❌ $service_name failed to start within ${max_wait}s${NC}"
    return 1
}

echo -e "${BLUE}🚀 Ollama Installation with Validation${NC}"
echo "=================================================="
echo ""

# Step 1: Check if ollama user exists, create if not
if ! run_ssh_command "STEP_01" "Step 1: Check/Create ollama user" \
    "id ollama || useradd -r -s /bin/false -d /opt/ollama ollama" \
    "id ollama"; then
    echo -e "${RED}Failed to create ollama user${NC}"
    exit 1
fi

# Step 2: Create ollama home directory
if ! run_ssh_command "STEP_02" "Step 2: Create ollama directory" \
    "mkdir -p /opt/ollama && chown ollama:ollama /opt/ollama" \
    "[ -d /opt/ollama ] && [ \$(stat -c %U /opt/ollama) = 'ollama' ]"; then
    echo -e "${RED}Failed to create ollama directory${NC}"
    exit 1
fi

# Step 3: Download and install Ollama binary manually
if ! run_ssh_command "STEP_03" "Step 3: Download Ollama binary" \
    "curl -L https://github.com/ollama/ollama/releases/download/v0.1.32/ollama-linux-amd64 -o /tmp/ollama && chmod +x /tmp/ollama && mv /tmp/ollama /usr/local/bin/ollama" \
    "[ -f /usr/local/bin/ollama ] && /usr/local/bin/ollama --version"; then
    echo -e "${RED}Failed to install Ollama binary${NC}"
    exit 1
fi

# Step 4: Create systemd service file
if ! run_ssh_command "STEP_04" "Step 4: Create systemd service" \
    "cat > /etc/systemd/system/ollama.service << 'EOL'
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
EOL" \
    "[ -f /etc/systemd/system/ollama.service ]"; then
    echo -e "${RED}Failed to create systemd service${NC}"
    exit 1
fi

# Step 5: Reload systemd and enable service
if ! run_ssh_command "STEP_05" "Step 5: Enable ollama service" \
    "systemctl daemon-reload && systemctl enable ollama" \
    "systemctl is-enabled ollama"; then
    echo -e "${RED}Failed to enable ollama service${NC}"
    exit 1
fi

# Step 6: Start ollama service
if ! run_ssh_command "STEP_06" "Step 6: Start ollama service" \
    "systemctl start ollama" \
    ""; then
    echo -e "${RED}Failed to start ollama service${NC}"
    exit 1
fi

# Step 7: Wait for service to be ready
update_progress "STEP_07" "IN_PROGRESS" "Waiting for service to be ready"
if ! wait_for_service "ollama" 30; then
    echo -e "${RED}Ollama service failed to start properly${NC}"
    update_progress "STEP_07" "FAILED" "Service failed to start within 30s"
    ssh -i ../private_key root@10.14.190.5 "systemctl status ollama --no-pager"
    exit 1
else
    update_progress "STEP_07" "COMPLETED" "Service ready and running"
fi

# Step 8: Configure firewall
if ! run_ssh_command "STEP_08" "Step 8: Configure firewall" \
    "firewall-cmd --permanent --add-port=11434/tcp && firewall-cmd --reload" \
    "firewall-cmd --list-ports | grep -q 11434"; then
    echo -e "${RED}Failed to configure firewall${NC}"
    exit 1
fi

# Step 9: Test API endpoint
if ! run_ssh_command "STEP_09" "Step 9: Test API endpoint" \
    "curl -s http://localhost:11434/api/tags" \
    "curl -s http://localhost:11434/api/tags | grep -q models"; then
    echo -e "${RED}Failed to connect to Ollama API${NC}"
    exit 1
fi

# Step 10: Download Mistral model
echo -e "${BLUE}=== Step 10: Download Mistral model ===${NC}"
echo -e "${YELLOW}⏳ This may take several minutes...${NC}"
if ! run_ssh_command "STEP_10" "Downloading Mistral 7B model" \
    "ollama pull mistral:7b" \
    "ollama list | grep -q mistral"; then
    echo -e "${RED}Failed to download Mistral model${NC}"
    exit 1
fi

# Step 11: Test model response
if ! run_ssh_command "STEP_11" "Step 11: Test model response" \
    "echo 'Hello, can you respond?' | ollama run mistral:7b" \
    ""; then
    echo -e "${RED}Failed to test model response${NC}"
    exit 1
fi

# Step 12: Create health check script
if ! run_ssh_command "STEP_12" "Step 12: Create health check script" \
    "cat > /usr/local/bin/ollama_health_check.sh << 'EOL'
#!/bin/bash
echo \"=== Ollama Health Check ===\$(date) ===\"

# Check service status
if systemctl is-active --quiet ollama; then
    echo \"✅ Service: Running\"
else
    echo \"❌ Service: Not running\"
    exit 1
fi

# Check API response
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo \"✅ API: Responding\"
else
    echo \"❌ API: Not responding\"
    exit 1
fi

# Check model availability
if ollama list | grep -q mistral:7b; then
    echo \"✅ Model: mistral:7b available\"
else
    echo \"❌ Model: mistral:7b not found\"
    exit 1
fi

echo \"✅ Ollama is healthy\"
EOL
chmod +x /usr/local/bin/ollama_health_check.sh" \
    "[ -x /usr/local/bin/ollama_health_check.sh ]"; then
    echo -e "${RED}Failed to create health check script${NC}"
    exit 1
fi

# Final health check
echo -e "${BLUE}=== Final Health Check ===${NC}"
update_progress "FINAL_CHECK" "IN_PROGRESS" "Running final system verification"
ssh -i ../private_key root@10.14.190.5 "/usr/local/bin/ollama_health_check.sh"

if [ $? -eq 0 ]; then
    update_progress "FINAL_CHECK" "COMPLETED" "All systems healthy and ready"
    echo ""
    echo -e "${GREEN}🎉 Ollama installation completed successfully!${NC}"
    echo "=================================================="
    echo ""
    echo -e "${BLUE}📋 Installation Summary:${NC}"
    echo "✅ Ollama service running on port 11434"
    echo "✅ Mistral 7B model downloaded and ready"
    echo "✅ Firewall configured for port 11434"
    echo "✅ Health check script created"
    echo ""
    echo -e "${BLUE}📞 Quick Commands:${NC}"
    echo "# Check service status:"
    echo "ssh -i ../private_key root@10.14.190.5 'systemctl status ollama'"
    echo ""
    echo "# Test model:"
    echo "ssh -i ../private_key root@10.14.190.5 'ollama run mistral:7b \"Hello\"'"
    echo ""
    echo "# Health check:"
    echo "ssh -i ../private_key root@10.14.190.5 '/usr/local/bin/ollama_health_check.sh'"
else
    update_progress "FINAL_CHECK" "FAILED" "Health check failed"
    echo -e "${RED}❌ Installation completed but health check failed${NC}"
    exit 1
fi 