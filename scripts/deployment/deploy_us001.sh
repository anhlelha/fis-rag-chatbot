#!/bin/bash
# Quick Start Script for US-001: Local LLM Setup
# Epic 1 - Proof of Concept

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 US-001: Local LLM Setup Deployment${NC}"
echo "=================================================="

# Check if running on Windows (Git Bash)
if [[ "$OSTYPE" == "msys" ]]; then
    echo -e "${YELLOW}⚠️  Detected Windows environment${NC}"
    echo "This script is designed for Linux/macOS. For Windows:"
    echo "1. Use WSL (Windows Subsystem for Linux)"
    echo "2. Or run the remote deployment script directly"
    echo ""
    echo -e "${GREEN}Option 1: Use WSL${NC}"
    echo "  wsl ./quick-start-us001.sh"
    echo ""
    echo -e "${GREEN}Option 2: Direct Remote Deployment${NC}"
    echo "  cd scripts"
    echo "  ./remote_deploy.sh config"
    echo "  ./remote_deploy.sh"
    echo ""
    read -p "Press Enter to continue with direct deployment..."
    ./remote_deploy.sh
    exit 0
fi

# Main deployment for Linux/macOS
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check required tools
REQUIRED_TOOLS=("ssh" "scp" "curl")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        echo -e "${RED}❌ Required tool not found: $tool${NC}"
        exit 1
    fi
done

# Check for sshpass if we might need it
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}⚠️  sshpass not found. Installing...${NC}"
    
    # Try to install sshpass
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y sshpass
    elif command -v yum &> /dev/null; then
        sudo yum install -y sshpass
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y sshpass
    elif command -v brew &> /dev/null; then
        brew install hudochenkov/sshpass/sshpass
    else
        echo -e "${YELLOW}⚠️  Please install sshpass manually if using password authentication${NC}"
    fi
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"
echo ""

# Make scripts executable (already in scripts directory)
chmod +x setup_ollama_centos8.sh remote_deploy.sh

echo -e "${BLUE}🔧 Starting deployment process...${NC}"
echo ""

# Run the deployment
echo -e "${GREEN}Running remote deployment script...${NC}"
./remote_deploy.sh

echo ""
echo -e "${GREEN}🎉 US-001 deployment completed!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Verify the installation using: ./remote_deploy.sh verify"
echo "2. Check the deployment guide: ../docs/deployment/us-001-deployment-guide.md"
echo "3. Mark US-001 as complete in Epic 1"
echo "4. Proceed to US-002: Document Processing Pipeline"
echo ""
echo -e "${YELLOW}📖 For detailed instructions, see:${NC}"
echo "   ../docs/deployment/us-001-deployment-guide.md" 