#!/bin/bash
# Quick Start for US-001: Local LLM Setup
# This script calls the main deployment script in scripts/ directory

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 US-001: Local LLM Setup - Quick Start${NC}"
echo "=================================================="
echo ""

# Check if scripts directory exists
if [ ! -d "scripts" ]; then
    echo -e "${RED}❌ Scripts directory not found!${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if the deployment script exists
if [ ! -f "scripts/deploy_us001.sh" ]; then
    echo -e "${RED}❌ Deployment script not found!${NC}"
    echo "Expected: scripts/deploy_us001.sh"
    exit 1
fi

echo -e "${GREEN}📁 Executing deployment script...${NC}"
echo ""

# Make the script executable and run it
chmod +x scripts/deploy_us001.sh
cd scripts
./deploy_us001.sh

echo ""
echo -e "${GREEN}🎉 Quick start completed!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}📖 For detailed instructions, see:${NC}"
echo "   docs/deployment/us-001-deployment-guide.md" 