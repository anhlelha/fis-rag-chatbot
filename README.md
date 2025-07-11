# 🤖 RAG Internal AI Copilot

**On-premises RAG AI solution with Vietnamese & English support**
---

ssh -i private_key root@10.14.190.5

## 📊 **Project Dashboard** ⭐

**👉 [View Complete Project Dashboard](docs/project-dashboard.md)**

Real-time tracking of all Epics, User Stories, progress, and KPIs.

---

## 🚀 Quick Start

### **Current Status**: Epic 1 - US-001 Deployment

```bash
# 1. Navigate to project
cd "03. FIS Internal ChatBot"

# 2. Deploy US-001 (Recommended)
cd scripts
./install_with_validation.sh

# 3. Monitor progress
./generate_progress_report.sh
./update_dashboard.sh
```

---

## 📂 Project Structure

```
RAG Internal AI Copilot/
├── 📊 docs/project-dashboard.md     # Main project dashboard
├── 📚 docs/                        # All documentation
│   ├── deployment/                 # Deployment guides & progress
│   ├── stories/                    # Epic & User Story planning  
│   ├── architecture/               # Technical architecture
│   └── prd/                        # Product requirements
├── 🔧 scripts/                     # Deployment automation
│   ├── install_with_validation.sh  # Recommended deployment
│   ├── update_dashboard.sh         # Dashboard auto-updater
│   └── generate_progress_report.sh # Progress reporting
├── 🚀 quick-start-us001.sh         # One-click deployment
└── .bmad-core/                     # Core configuration
```

---

## 🎯 Project Overview

| **Epic** | **Status** | **Timeline** | **Budget** | **Stories** |
|----------|------------|--------------|------------|-------------|
| **Epic 1** - Proof of Concept | 🔄 **85% Complete** | Week 1 | $30K | 6 stories |
| **Epic 2** - Internal Rollout | ⏳ **Planned** | Week 2-4 | $100K | 6 stories |
| **Epic 3** - Expansion & Scale | ⏳ **Planned** | Week 5-12 | $200K | 6 stories |

**Total Budget**: $330K | **Timeline**: 12 weeks | **Target**: 200+ users

---

## 🔥 Current Focus: US-001 Local LLM Setup

**Objective**: Deploy Ollama + Mistral 7B on CentOS 8 server

**Progress**: 🔄 **85% Complete**
- ✅ Requirements & Planning
- ✅ CentOS 8 Server Setup  
- 🔄 Ollama Installation \(in progress\)
- ⏳ Model Testing & Validation
- ⏳ Performance Testing

**Next Steps**:
1. Complete Ollama deployment validation
2. Begin US-002: Document Processing Pipeline
3. Prepare for stakeholder demo

---

## 📋 Key Resources

### **📊 Dashboards & Reports**
- [📊 **Project Dashboard**](docs/project-dashboard.md) - Main project overview
- [📈 **US-001 Progress**](docs/deployment/us-001-progress-report.md) - Current deployment status  
- [📝 **Installation Checklist**](docs/deployment/us-001-installation-checklist.md) - Detailed steps

### **📚 Documentation**
- [🎯 **Epic 1 Planning**](docs/stories/epic-01-proof-of-concept.md) - PoC requirements
- [🏗️ **Master Plan**](docs/stories/project-master-plan.md) - Complete project plan
- [💼 **Executive Summary**](docs/stories/executive-summary.md) - Business overview
- [🌐 **Vietnamese Guide**](docs/stories/README-vi.md) - Hướng dẫn tiếng Việt

### **🔧 Deployment**
- [🚀 **Deployment Guides**](docs/deployment/README.md) - All deployment documentation
- [⚙️ **Scripts Documentation**](scripts/README.md) - Automation scripts guide
- [📦 **US-001 Deployment**](docs/deployment/us-001-deployment-guide.md) - CentOS 8 setup guide

---

## 🛠️ Technology Stack

### **Core Components**
- **LLM**: Ollama + Mistral 7B \(on-premises\)
- **Server**: CentOS 8 \(31GB RAM, 16 CPUs\)
- **RAG Framework**: LangChain
- **Vector DB**: FAISS / ChromaDB
- **UI**: Streamlit / Gradio
- **Languages**: Vietnamese + English

### **Infrastructure**
- **Deployment**: SSH automation scripts
- **Monitoring**: Health checks + progress tracking
- **Security**: On-premises, no external API calls
- **Scale**: 200+ concurrent users target

---

## 👥 Team & Roles

| **Role** | **Epic 1** | **Epic 2** | **Epic 3** |
|----------|------------|------------|------------|
| **System Admin** | US-001 CentOS 8 | Production infra | Load balancing |
| **Backend Dev** | RAG pipeline | Performance opt | Business integration |
| **Frontend Dev** | Basic UI | Enhanced UI | Advanced features |
| **Data Curator** | Doc processing | Doc sync | Analytics |
| **Product Owner** | Demo prep | User mgmt | Change mgmt |
| **QA Engineer** | Testing | QA testing | Enterprise testing |

---

## 🚨 Important Notes

### **For Stakeholders**
- **Demo Ready**: End of Week 1 \(Epic 1\)
- **Beta Launch**: End of Week 4 \(Epic 2\)
- **Production**: End of Week 8 \(Epic 3\)
- **ROI Expected**: 300% within 18 months

### **For Developers**
- **Current Sprint**: Epic 1 - Sprint 1
- **Active Story**: US-001 \(Local LLM Setup\)
- **Next Story**: US-002 \(Document Processing\)
- **Server**: CentOS 8 \(IP: 10.14.190.5\)

### **For Operations**
- **Monitoring**: `scripts/generate_progress_report.sh`
- **Updates**: `scripts/update_dashboard.sh`
- **Health Check**: `/usr/local/bin/ollama_health_check.sh`
- **Logs**: `scripts/installation_progress.log`

---

## 📞 Support & Contact

### **Issues & Questions**
1. **📊 Check Dashboard**: [docs/project-dashboard.md](docs/project-dashboard.md)
2. **🔧 Check Scripts**: [scripts/README.md](scripts/README.md)  
3. **📚 Check Deployment Guide**: [docs/deployment/](docs/deployment/)
4. **👥 Contact Team**: Development Team

### **Quick Commands**
```bash
# Check current status
cd scripts && ./generate_progress_report.sh

# Update dashboard  
./update_dashboard.sh

# Deploy US-001
./install_with_validation.sh

# Health check server
ssh -i ../private_key root@10.14.190.5 '/usr/local/bin/ollama_health_check.sh'
```

---

## 🎯 Success Metrics

- **✅ On-premises LLM**: No external API dependencies
- **🌐 Bilingual Support**: Vietnamese + English queries
- **⚡ Performance**: <15 second response time
- **📈 Scale**: 200+ concurrent users
- **🔒 Security**: Enterprise-grade on-premises
- **💰 ROI**: 300% return within 18 months

---

**Project Status**: 🟢 **Active Development**  
**Last Updated**: Auto-updated via dashboard  
**Next Milestone**: Epic 1 Demo \(End of Week 1\)

---

*💡 **Pro Tip**: Bookmark the [📊 Project Dashboard](docs/project-dashboard.md) for real-time project status!* 