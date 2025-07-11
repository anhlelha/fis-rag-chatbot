#!/bin/bash
# Ollama Setup Script for CentOS 8
# Epic 1 - US-001: Local LLM Setup

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLLAMA_VERSION="latest"
OLLAMA_PORT="11434"
OLLAMA_USER="ollama"
OLLAMA_HOME="/opt/ollama"
MODEL_NAME="mistral:7b"

# Logging function
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check OS version
    if ! grep -q "CentOS Linux release 8" /etc/redhat-release 2>/dev/null; then
        if ! grep -q "Rocky Linux release 8" /etc/redhat-release 2>/dev/null; then
            error "This script is designed for CentOS 8 or Rocky Linux 8"
        fi
    fi
    
    # Check memory (minimum 8GB)
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -lt 8 ]; then
        error "Minimum 8GB RAM required. Current: ${TOTAL_MEM}GB"
    fi
    
    # Check available disk space (minimum 20GB)
    AVAILABLE_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 20 ]; then
        error "Minimum 20GB disk space required. Available: ${AVAILABLE_SPACE}GB"
    fi
    
    # Check CPU cores (minimum 2)
    CPU_CORES=$(nproc)
    if [ "$CPU_CORES" -lt 2 ]; then
        error "Minimum 2 CPU cores required. Current: ${CPU_CORES}"
    fi
    
    success "System requirements check passed"
    log "Memory: ${TOTAL_MEM}GB, Disk: ${AVAILABLE_SPACE}GB, CPUs: ${CPU_CORES}"
}

# Function to update system
update_system() {
    log "Updating system packages..."
    
    # Update package manager
    sudo dnf update -y
    
    # Install required packages
    sudo dnf install -y \
        curl \
        wget \
        unzip \
        htop \
        net-tools \
        firewalld \
        systemd
    
    success "System updated and required packages installed"
}

# Function to create ollama user
create_ollama_user() {
    log "Creating ollama user..."
    
    if ! id "$OLLAMA_USER" &>/dev/null; then
        sudo useradd -r -s /bin/false -d "$OLLAMA_HOME" "$OLLAMA_USER"
        success "User $OLLAMA_USER created"
    else
        warning "User $OLLAMA_USER already exists"
    fi
    
    # Create ollama home directory
    sudo mkdir -p "$OLLAMA_HOME"
    sudo chown "$OLLAMA_USER":"$OLLAMA_USER" "$OLLAMA_HOME"
    
    success "Ollama user and directory setup completed"
}

# Function to install Ollama
install_ollama() {
    log "Installing Ollama..."
    
    # Download and install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    # Verify installation
    if command_exists ollama; then
        success "Ollama installed successfully"
        ollama --version
    else
        error "Ollama installation failed"
    fi
}

# Function to configure systemd service
configure_systemd_service() {
    log "Configuring systemd service..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=$OLLAMA_USER
Group=$OLLAMA_USER
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:$OLLAMA_PORT"
Environment="OLLAMA_ORIGINS=*"

[Install]
WantedBy=default.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable ollama
    
    success "Systemd service configured"
}

# Function to configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    # Start firewalld if not running
    sudo systemctl start firewalld
    sudo systemctl enable firewalld
    
    # Open port for Ollama
    sudo firewall-cmd --permanent --add-port=$OLLAMA_PORT/tcp
    sudo firewall-cmd --reload
    
    success "Firewall configured to allow port $OLLAMA_PORT"
}

# Function to start Ollama service
start_ollama_service() {
    log "Starting Ollama service..."
    
    sudo systemctl start ollama
    
    # Wait for service to start
    sleep 5
    
    # Check service status
    if sudo systemctl is-active ollama &>/dev/null; then
        success "Ollama service started successfully"
    else
        error "Failed to start Ollama service"
    fi
}

# Function to download and test model
download_and_test_model() {
    log "Downloading model: $MODEL_NAME"
    
    # Download model
    ollama pull "$MODEL_NAME"
    
    success "Model $MODEL_NAME downloaded successfully"
    
    # Test model with Vietnamese query
    log "Testing model with Vietnamese query..."
    VIETNAMESE_TEST="Xin chào, bạn có thể trả lời câu hỏi bằng tiếng Việt không?"
    RESPONSE=$(ollama run "$MODEL_NAME" "$VIETNAMESE_TEST")
    
    if [[ -n "$RESPONSE" ]]; then
        success "Vietnamese test passed"
        log "Response: $RESPONSE"
    else
        error "Vietnamese test failed"
    fi
    
    # Test model with English query
    log "Testing model with English query..."
    ENGLISH_TEST="Hello, can you answer questions in English?"
    RESPONSE=$(ollama run "$MODEL_NAME" "$ENGLISH_TEST")
    
    if [[ -n "$RESPONSE" ]]; then
        success "English test passed"
        log "Response: $RESPONSE"
    else
        error "English test failed"
    fi
}

# Function to create health check script
create_health_check() {
    log "Creating health check script..."
    
    sudo tee /usr/local/bin/ollama_health_check.sh > /dev/null <<'EOF'
#!/bin/bash
# Ollama Health Check Script

OLLAMA_HOST="localhost:11434"
MODEL_NAME="mistral:7b"

# Check if Ollama service is running
if ! systemctl is-active ollama &>/dev/null; then
    echo "❌ Ollama service is not running"
    exit 1
fi

# Check if Ollama API is responding
if ! curl -s "http://$OLLAMA_HOST/api/tags" > /dev/null; then
    echo "❌ Ollama API is not responding"
    exit 1
fi

# Check if model is available
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "❌ Model $MODEL_NAME is not available"
    exit 1
fi

# Test model response
TEST_QUERY="Test query"
RESPONSE=$(timeout 30 ollama run "$MODEL_NAME" "$TEST_QUERY" 2>/dev/null)

if [[ -n "$RESPONSE" ]]; then
    echo "✅ Ollama is healthy"
    echo "   - Service: Running"
    echo "   - API: Responding"
    echo "   - Model: $MODEL_NAME available"
    echo "   - Response time: <30 seconds"
    exit 0
else
    echo "❌ Model is not responding properly"
    exit 1
fi
EOF
    
    sudo chmod +x /usr/local/bin/ollama_health_check.sh
    
    success "Health check script created at /usr/local/bin/ollama_health_check.sh"
}

# Function to display setup summary
display_summary() {
    log "Setup Summary:"
    echo "============================================"
    echo "✅ Ollama installed and configured"
    echo "✅ Model: $MODEL_NAME downloaded"
    echo "✅ Service: Running on port $OLLAMA_PORT"
    echo "✅ Firewall: Port $OLLAMA_PORT opened"
    echo "✅ Health check: Available"
    echo "============================================"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • Check service status: sudo systemctl status ollama"
    echo "  • View logs: sudo journalctl -u ollama -f"
    echo "  • Health check: /usr/local/bin/ollama_health_check.sh"
    echo "  • Test model: ollama run $MODEL_NAME"
    echo "  • List models: ollama list"
    echo ""
    echo "🌐 API Endpoint: http://$(hostname -I | awk '{print $1}'):$OLLAMA_PORT"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Test the health check script"
    echo "  2. Verify model responses in Vietnamese and English"
    echo "  3. Proceed to US-002: Document Processing Pipeline"
}

# Main installation function
main() {
    log "Starting Ollama installation on CentOS 8..."
    log "Epic 1 - US-001: Local LLM Setup"
    
    check_requirements
    update_system
    create_ollama_user
    install_ollama
    configure_systemd_service
    configure_firewall
    start_ollama_service
    download_and_test_model
    create_health_check
    
    success "Ollama installation completed successfully!"
    display_summary
}

# Run main function
main "$@" 