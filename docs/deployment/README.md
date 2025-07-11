# 📁 Deployment Guides

This directory contains detailed deployment guides for implementing each User Story in the RAG AI Copilot project.

## 📂 Directory Structure

```
docs/deployment/
├── README.md                    # This file
├── us-001-deployment-guide.md   # Local LLM Setup on CentOS 8
├── us-002-deployment-guide.md   # Document Processing Pipeline (future)
├── us-003-deployment-guide.md   # Vector Database Implementation (future)
├── us-004-deployment-guide.md   # RAG Query Pipeline (future)
├── us-005-deployment-guide.md   # Basic User Interface (future)
└── us-006-deployment-guide.md   # Demo Preparation (future)
```

## 🎯 Purpose

Each deployment guide provides:
- **Step-by-step instructions** for implementing specific User Stories
- **Technical configurations** for servers and systems
- **Verification procedures** to ensure successful deployment
- **Troubleshooting guides** for common issues
- **Success criteria checklists** for acceptance testing

## 📋 Available Guides

### Epic 1: Proof of Concept

#### ✅ US-001: Local LLM Setup
- **File**: `us-001-deployment-guide.md`
- **Purpose**: Deploy Ollama with Mistral model on CentOS 8 server
- **Duration**: 30-60 minutes
- **Dependencies**: CentOS 8 server with SSH access
- **Status**: Ready for deployment

#### 🔄 US-002: Document Processing Pipeline
- **File**: `us-002-deployment-guide.md` \(coming soon\)
- **Purpose**: Set up document processing with LangChain
- **Dependencies**: US-001 completion

#### 🔄 US-003: Vector Database Implementation
- **File**: `us-003-deployment-guide.md` \(coming soon\)
- **Purpose**: Deploy vector database and embedding models
- **Dependencies**: US-001, US-002 completion

#### 🔄 US-004: RAG Query Pipeline
- **File**: `us-004-deployment-guide.md` \(coming soon\)
- **Purpose**: Implement end-to-end RAG functionality
- **Dependencies**: US-001, US-002, US-003 completion

#### 🔄 US-005: Basic User Interface
- **File**: `us-005-deployment-guide.md` \(coming soon\)
- **Purpose**: Deploy Streamlit/Gradio chat interface
- **Dependencies**: US-001 through US-004 completion

#### 🔄 US-006: Demo Preparation
- **File**: `us-006-deployment-guide.md` \(coming soon\)
- **Purpose**: Prepare comprehensive stakeholder demo
- **Dependencies**: All previous US completion

## 🚀 Quick Start

### For US-001 \(Currently Available\):
```bash
# Navigate to project root
cd "03. FIS Internal ChatBot"

# Quick deployment (from project root)
./quick-start-us001.sh

# Or run directly from scripts directory
cd scripts
./install_with_validation.sh  # Recommended - with progress tracking

# Alternative deployment methods
./deploy_us001.sh              # Basic deployment
./remote_deploy.sh config      # Manual configuration
./remote_deploy.sh             # Manual deployment

# Verify deployment
./remote_deploy.sh verify

# Check installation progress
cd scripts
./generate_progress_report.sh  # Generate progress report
```

### For Future User Stories:
Each guide will include similar quick start commands when available.

## 📖 How to Use These Guides

### 1. **Before Starting**
- Review the Epic planning document in `docs/stories/`
- Ensure all prerequisites are met
- Prepare required server access and credentials

### 2. **During Deployment**
- Follow step-by-step instructions carefully
- Run verification commands after each major step
- Document any deviations or issues encountered

### 3. **After Deployment**
- Complete all verification steps
- Run health checks and performance tests
- Update project status and inform team
- Prepare for next User Story

### 4. **Troubleshooting**
- Each guide includes common issues and solutions
- Check logs and system status using provided commands
- Escalate to team if issues persist

## 🔗 Related Documentation

- **📊 Project Dashboard**: `docs/project-dashboard.md` ⭐ **MAIN OVERVIEW**
- **Epic Planning**: `docs/stories/epic-01-proof-of-concept.md`
- **Project Overview**: `docs/stories/README.md`
- **Executive Summary**: `docs/stories/executive-summary.md`
- **Master Plan**: `docs/stories/project-master-plan.md`

## 📞 Support

For deployment issues or questions:
1. Check the troubleshooting section in relevant guide
2. Review Epic documentation for context
3. Contact project team for assistance

---

**Directory Purpose**: Technical implementation guides  
**Target Audience**: Developers, System Administrators, DevOps Engineers  
**Update Frequency**: As each User Story is developed  
**Maintained By**: Development Team 