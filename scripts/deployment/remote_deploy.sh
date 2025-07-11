#!/bin/bash
# Remote Deployment Script for Ollama on CentOS 8
# Epic 1 - US-001: Local LLM Setup

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these values
SERVER_IP=""
SERVER_USER=""
SERVER_PASS=""
SSH_KEY_PATH=""

# Script paths
SETUP_SCRIPT="setup_ollama_centos8.sh"
REMOTE_SETUP_PATH="/tmp/setup_ollama_centos8.sh"

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Function to validate configuration
validate_config() {
    log "Validating configuration..."
    
    if [[ -z "$SERVER_IP" ]]; then
        error "SERVER_IP is not set. Please update the script configuration."
    fi
    
    if [[ -z "$SERVER_USER" ]]; then
        error "SERVER_USER is not set. Please update the script configuration."
    fi
    
    if [[ -z "$SERVER_PASS" && -z "$SSH_KEY_PATH" ]]; then
        error "Either SERVER_PASS or SSH_KEY_PATH must be set for authentication."
    fi
    
    if [[ -n "$SSH_KEY_PATH" && ! -f "$SSH_KEY_PATH" ]]; then
        error "SSH key file not found: $SSH_KEY_PATH"
    fi
    
    if [[ ! -f "$SETUP_SCRIPT" ]]; then
        error "Setup script not found: $SETUP_SCRIPT"
    fi
    
    success "Configuration validation passed"
}

# Function to test SSH connection
test_ssh_connection() {
    log "Testing SSH connection to $SERVER_USER@$SERVER_IP..."
    
    if [[ -n "$SSH_KEY_PATH" ]]; then
        # Test with SSH key
        if ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo 'SSH connection successful'" >/dev/null 2>&1; then
            success "SSH connection test passed (using SSH key)"
        else
            error "SSH connection failed with key: $SSH_KEY_PATH"
        fi
    else
        # Test with password (using sshpass)
        if ! command -v sshpass >/dev/null 2>&1; then
            error "sshpass not found. Install it: sudo apt-get install sshpass"
        fi
        
        if sshpass -p "$SERVER_PASS" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo 'SSH connection successful'" >/dev/null 2>&1; then
            success "SSH connection test passed (using password)"
        else
            error "SSH connection failed with password"
        fi
    fi
}

# Function to copy setup script to remote server
copy_setup_script() {
    log "Copying setup script to remote server..."
    
    if [[ -n "$SSH_KEY_PATH" ]]; then
        # Copy with SSH key
        scp -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SETUP_SCRIPT" "$SERVER_USER@$SERVER_IP:$REMOTE_SETUP_PATH"
    else
        # Copy with password
        sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no "$SETUP_SCRIPT" "$SERVER_USER@$SERVER_IP:$REMOTE_SETUP_PATH"
    fi
    
    success "Setup script copied to remote server"
}

# Function to execute setup script on remote server
execute_remote_setup() {
    log "Executing setup script on remote server..."
    
    if [[ -n "$SSH_KEY_PATH" ]]; then
        # Execute with SSH key
        ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
            chmod +x /tmp/setup_ollama_centos8.sh
            sudo /tmp/setup_ollama_centos8.sh
EOF
    else
        # Execute with password
        sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
            chmod +x /tmp/setup_ollama_centos8.sh
            sudo /tmp/setup_ollama_centos8.sh
EOF
    fi
    
    success "Setup script executed successfully"
}

# Function to verify installation
verify_installation() {
    log "Verifying Ollama installation..."
    
    if [[ -n "$SSH_KEY_PATH" ]]; then
        # Verify with SSH key
        HEALTH_CHECK=$(ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "/usr/local/bin/ollama_health_check.sh" 2>/dev/null || echo "FAILED")
    else
        # Verify with password
        HEALTH_CHECK=$(sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "/usr/local/bin/ollama_health_check.sh" 2>/dev/null || echo "FAILED")
    fi
    
    if [[ "$HEALTH_CHECK" == *"✅ Ollama is healthy"* ]]; then
        success "Ollama installation verified successfully"
        log "Health check output:"
        echo "$HEALTH_CHECK"
    else
        error "Ollama installation verification failed"
    fi
}

# Function to display deployment summary
display_deployment_summary() {
    log "Deployment Summary:"
    echo "============================================"
    echo "✅ Remote deployment completed successfully"
    echo "✅ Server: $SERVER_USER@$SERVER_IP"
    echo "✅ Ollama service: Running"
    echo "✅ Model: mistral:7b downloaded"
    echo "✅ Health check: Passed"
    echo "============================================"
    echo ""
    echo "🔧 Remote Commands:"
    echo "  • SSH login: ssh $SERVER_USER@$SERVER_IP"
    echo "  • Check status: sudo systemctl status ollama"
    echo "  • View logs: sudo journalctl -u ollama -f"
    echo "  • Health check: /usr/local/bin/ollama_health_check.sh"
    echo "  • Test model: ollama run mistral:7b"
    echo ""
    echo "🌐 API Endpoint: http://$SERVER_IP:11434"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Access the server and run additional tests"
    echo "  2. Update US-001 checklist items"
    echo "  3. Proceed to US-002: Document Processing Pipeline"
}

# Function to prompt for configuration
prompt_for_config() {
    log "Please provide server connection details:"
    
    read -p "Server IP address: " SERVER_IP
    read -p "Server username: " SERVER_USER
    
    echo "Choose authentication method:"
    echo "1) SSH Key"
    echo "2) Password"
    read -p "Enter choice (1 or 2): " AUTH_METHOD
    
    if [[ "$AUTH_METHOD" == "1" ]]; then
        read -p "SSH key path (default: ~/.ssh/id_rsa): " SSH_KEY_PATH
        SSH_KEY_PATH="${SSH_KEY_PATH:-$HOME/.ssh/id_rsa}"
    else
        read -s -p "Server password: " SERVER_PASS
        echo
    fi
    
    success "Configuration collected"
}

# Function to save configuration
save_config() {
    log "Saving configuration to config file..."
    
    cat > server_config.sh << EOF
#!/bin/bash
# Server Configuration for Ollama Deployment
# Generated on $(date)

export SERVER_IP="$SERVER_IP"
export SERVER_USER="$SERVER_USER"
export SERVER_PASS="$SERVER_PASS"
export SSH_KEY_PATH="$SSH_KEY_PATH"
EOF
    
    chmod 600 server_config.sh
    success "Configuration saved to server_config.sh"
}

# Function to load configuration
load_config() {
    if [[ -f "server_config.sh" ]]; then
        log "Loading configuration from server_config.sh..."
        source server_config.sh
        success "Configuration loaded"
    fi
}

# Main deployment function
main() {
    log "Starting remote deployment of Ollama on CentOS 8..."
    log "Epic 1 - US-001: Local LLM Setup"
    
    # Load existing config if available
    load_config
    
    # Prompt for config if not already set
    if [[ -z "$SERVER_IP" ]]; then
        prompt_for_config
        save_config
    fi
    
    validate_config
    test_ssh_connection
    copy_setup_script
    execute_remote_setup
    verify_installation
    
    success "Remote deployment completed successfully!"
    display_deployment_summary
}

# Handle command line arguments
case "${1:-}" in
    "config")
        prompt_for_config
        save_config
        ;;
    "verify")
        load_config
        verify_installation
        ;;
    "")
        main
        ;;
    *)
        echo "Usage: $0 [config|verify]"
        echo "  config - Set up server connection configuration"
        echo "  verify - Verify existing installation"
        echo "  (no args) - Run full deployment"
        exit 1
        ;;
esac 