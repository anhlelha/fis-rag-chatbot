# Epic 1: RAG AI Copilot Proof of Concept

## Epic Information
- **Epic ID**: EP-001
- **Epic Name**: RAG AI Copilot Proof of Concept
- **Duration**: 1 week
- **Priority**: P0 (Critical)
- **Objective**: Validate RAG concept with local LLM for internal document search

---

## Epic Overview

Build a minimal viable RAG system to demonstrate the feasibility of using local LLM with company documents. This proof of concept will validate the technical approach and business value before larger investment.

### Business Value
- **Validate concept** with real internal documents
- **Demonstrate security** with on-premises deployment
- **Test user experience** with natural language queries
- **Establish baseline performance** metrics
- **Get stakeholder buy-in** for full implementation

### Success Criteria
- ✅ System can answer questions from 10 internal documents
- ✅ Average response time <15 seconds
- ✅ Users can successfully query in Vietnamese and English
- ✅ No data transmitted outside company network
- ✅ Demo completed to stakeholders

---

## User Stories

### Story 1: Local LLM Setup

**US-001**: As a **System Administrator**, I want to **set up Ollama with local LLM** so that **we can process queries without external API calls**.

#### Acceptance Criteria:
- [ ] Ollama installed and running on CentOS 8 server
- [ ] Mistral 7B model downloaded and functional
- [ ] LLM responds to basic prompts in Vietnamese and English
- [ ] System uses only local compute resources on CentOS 8
- [ ] No network calls to external LLM services
- [ ] Systemd service configured for auto-start on boot
- [ ] Firewall properly configured for port 11434
- [ ] Health check script operational
- [ ] Remote deployment scripts tested successfully

#### Technical Tasks:
```bash
# Installation tasks for CentOS 8
- [ ] Install Ollama on CentOS 8 server
- [ ] Download mistral:7b model (`ollama pull mistral`)
- [ ] Test basic LLM functionality
- [ ] Configure memory allocation (8GB minimum)
- [ ] Verify CPU-only operation
- [ ] Set up systemd service for auto-start
- [ ] Configure firewall for port 11434
```

#### Definition of Done:
- [ ] Ollama service running on port 11434 on CentOS 8 server
- [ ] Mistral 7B model responds to test queries within 10 seconds
- [ ] Vietnamese and English language support verified
- [ ] Systemd service configured for auto-start
- [ ] Firewall configured for port 11434
- [ ] Health check script implemented and tested
- [ ] Complete deployment documentation created
- [ ] Remote deployment scripts tested successfully

---

### Story 2: Document Processing Pipeline

**US-002**: As a **Content Manager**, I want to **process internal documents into searchable format** so that **the AI can find relevant information**.

#### Acceptance Criteria:
- [ ] System can process PDF, DOCX, and Excel files
- [ ] Documents are chunked into logical segments
- [ ] Text extraction preserves important context
- [ ] Metadata is captured (title, author, date)
- [ ] Processed content is stored for retrieval

#### Technical Tasks:
```python
# Document processing implementation
- [ ] Install LangChain document loaders
- [ ] Implement PDF processing (PyPDFLoader)
- [ ] Implement DOCX processing (DocxLoader)
- [ ] Implement Excel processing (PandasLoader)
- [ ] Create chunking strategy (500-1000 tokens)
- [ ] Add metadata extraction
```

#### Test Documents:
- [ ] 3 PDF policy documents
- [ ] 2 DOCX procedure manuals
- [ ] 2 Excel reports/templates
- [ ] 3 miscellaneous company documents

#### Definition of Done:
- [ ] All test documents processed successfully
- [ ] Chunks created with appropriate overlap
- [ ] Metadata extracted and stored
- [ ] Processing pipeline runs without errors
- [ ] Document stats logged (pages, chunks, tokens)

---

### Story 3: Vector Database Implementation

**US-003**: As a **Developer**, I want to **implement vector storage and search** so that **the system can find semantically similar content**.

#### Acceptance Criteria:
- [ ] Embedding model generates vectors for document chunks
- [ ] Vector database stores embeddings efficiently
- [ ] Similarity search returns relevant results
- [ ] Search performance is acceptable (<5 seconds)
- [ ] Vector store persists between sessions

#### Technical Tasks:
```python
# Vector implementation
- [ ] Install sentence-transformers or instructor
- [ ] Choose embedding model (all-MiniLM-L6-v2)
- [ ] Set up FAISS or Chroma vector store
- [ ] Implement batch embedding generation
- [ ] Create similarity search function
- [ ] Add persistence layer
```

#### Embedding Configuration:
```python
# Example configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIMENSION = 384
SIMILARITY_THRESHOLD = 0.7
MAX_RESULTS = 5
```

#### Definition of Done:
- [ ] Vector database contains all document embeddings
- [ ] Search returns relevant results in <5 seconds
- [ ] Vector store saves to disk successfully
- [ ] Similarity scores are meaningful (0.6-1.0 range)
- [ ] Memory usage is reasonable (<4GB)

---

### Story 4: RAG Query Pipeline

**US-004**: As a **End User**, I want to **ask questions in natural language** so that **I can get answers from company documents**.

#### Acceptance Criteria:
- [ ] System accepts questions in Vietnamese and English
- [ ] Relevant document chunks are retrieved
- [ ] LLM generates contextual answers
- [ ] Sources are cited in responses
- [ ] Response quality is satisfactory

#### Technical Tasks:
```python
# RAG pipeline implementation
- [ ] Implement query processing
- [ ] Create retrieval function
- [ ] Set up LLM prompt template
- [ ] Add source citation
- [ ] Implement response formatting
```

#### Sample Test Queries:
```
Vietnamese:
- "Quy trình nghỉ phép của công ty như thế nào?"
- "Chính sách làm việc từ xa ra sao?"

English:
- "What is the expense reimbursement process?"
- "How do I request IT equipment?"
```

#### Definition of Done:
- [ ] All sample queries return relevant answers
- [ ] Responses include document sources
- [ ] Average response time <15 seconds
- [ ] Answers are factual and helpful
- [ ] System handles both Vietnamese and English

---

### Story 5: Basic User Interface

**US-005**: As a **Business User**, I want to **interact with the AI through a simple interface** so that **I can easily ask questions and get answers**.

#### Acceptance Criteria:
- [ ] Web interface is accessible and intuitive
- [ ] Chat-style interaction is implemented
- [ ] Query history is maintained during session
- [ ] Responses are clearly formatted
- [ ] Interface works on desktop browsers

#### Technical Tasks:
```python
# UI implementation with Streamlit or Gradio
- [ ] Install Streamlit or Gradio
- [ ] Create chat interface layout
- [ ] Implement message history
- [ ] Add loading indicators
- [ ] Style for professional appearance
```

#### Interface Features:
- [ ] **Query Input**: Text area for questions
- [ ] **Response Display**: Formatted answers with sources
- [ ] **History Panel**: Previous questions and answers
- [ ] **Clear Function**: Reset conversation
- [ ] **Loading State**: Progress indicator during processing

#### Definition of Done:
- [ ] Interface accessible via web browser
- [ ] All features working without errors
- [ ] Professional appearance suitable for demo
- [ ] Response formatting is readable
- [ ] Session state maintained properly

---

### Story 6: Demo Preparation

**US-006**: As a **Product Owner**, I want to **prepare a comprehensive demo** so that **stakeholders can evaluate the system's potential**.

#### Acceptance Criteria:
- [ ] Demo script covers key use cases
- [ ] Test data represents real company scenarios
- [ ] Performance metrics are captured
- [ ] Demo environment is stable
- [ ] Feedback mechanism is in place

#### Demo Scenarios:
1. **HR Policy Query**: "What is our vacation policy?"
2. **IT Procedure**: "How do I reset my password?"
3. **Financial Process**: "What is the expense approval workflow?"
4. **Multilingual Test**: Vietnamese and English queries
5. **Source Verification**: Show document citations

#### Technical Tasks:
- [ ] Prepare demo dataset (10 documents)
- [ ] Create demo script with talking points
- [ ] Set up stable demo environment
- [ ] Implement basic analytics (query count, response time)
- [ ] Create feedback collection form

#### Definition of Done:
- [ ] Demo runs smoothly without technical issues
- [ ] All scenarios demonstrate value clearly
- [ ] Performance metrics are positive
- [ ] Stakeholder feedback is collected
- [ ] Next steps are defined

---

## Sprint Planning

### Sprint 1 (Days 1-3): Foundation Setup
- **US-001**: Local LLM Setup on CentOS 8 (1 day)
- **US-002**: Document Processing Pipeline (2 days)

### Sprint 2 (Days 4-5): Core RAG Implementation
- **US-003**: Vector Database Implementation (1 day)
- **US-004**: RAG Query Pipeline (1 day)

### Sprint 3 (Days 6-7): Interface and Demo
- **US-005**: Basic User Interface (1 day)
- **US-006**: Demo Preparation (1 day)

---

## Technical Architecture (PoC)

```
┌─────────────────────────────────────────────────────────┐
│                PoC Architecture on CentOS 8             │
├─────────────────────────────────────────────────────────┤
│ User Interface (Streamlit/Gradio)                      │
│ ┌─────────────────────────────────────────────────────┐ │
│ │     Chat Interface                                  │ │
│ │   - Query Input                                     │ │
│ │   - Response Display                                │ │
│ │   - Session History                                 │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ RAG Engine (LangChain)                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │   Query     │ │  Retrieval  │ │  Response   │       │
│ │ Processing  │ │   Engine    │ │ Generation  │       │
│ │             │ │             │ │             │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
├─────────────────────────────────────────────────────────┤
│ Data Layer (CentOS 8 Server)                           │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │   Vector    │ │  Documents  │ │    Ollama   │       │
│ │ Store (FAISS│ │ Processing  │ │  + Mistral  │       │
│ │ /Chroma)    │ │ (LangChain) │ │ Port: 11434 │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
├─────────────────────────────────────────────────────────┤
│ CentOS 8 Infrastructure                                │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │   Systemd   │ │  Firewall   │ │  Health     │       │
│ │   Service   │ │   (11434)   │ │   Check     │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## Resource Requirements

### CentOS 8 Server Specifications
- **OS**: CentOS 8 or Rocky Linux 8
- **CPU**: 4+ cores (Intel i5/Ryzen 5 or better)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 30GB SSD for models and data
- **Network**: Internal network access only
- **Access**: SSH access with sudo privileges

### CentOS 8 System Dependencies
```bash
# System packages (installed via dnf)
curl
wget
unzip
htop
net-tools
firewalld
systemd
python3
python3-pip

# Ollama installation
ollama>=0.1.0          # Installed via official script
mistral:7b            # Downloaded via: ollama pull mistral
```

### Development Dependencies (for local development)
```bash
# Core Python dependencies
langchain>=0.1.0
streamlit>=1.28.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0  # or chromadb>=0.4.0

# Document processing
pypdf>=3.17.0
python-docx>=0.8.11
pandas>=2.0.0
openpyxl>=3.1.0
```

### Team Requirements
- **1 System Administrator**: CentOS 8 server setup and Ollama deployment
- **1 Developer**: RAG pipeline development and testing
- **1 Data Curator**: Document preparation and testing
- **1 Product Owner**: Requirements and demo coordination

---

## Risk Mitigation

### Technical Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| **LLM Performance on CentOS 8** | Medium | High | Test multiple models, optimize prompts |
| **CentOS 8 Compatibility** | Low | Medium | Use official Ollama installation script |
| **Memory Usage on Server** | Medium | Medium | Monitor usage, optimize chunking |
| **Query Accuracy** | High | High | Iterate on retrieval and prompt engineering |
| **Network/Firewall Issues** | Low | Medium | Proper firewall configuration and testing |
| **SSH Access Problems** | Low | High | Test SSH connectivity before deployment |

### Business Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| **Stakeholder Expectations** | Medium | High | Set clear demo scope and limitations |
| **Security Concerns** | Low | High | Emphasize on-premises CentOS 8 deployment |
| **Resource Allocation** | Low | Medium | Document minimal resource requirements |
| **Server Availability** | Low | High | Ensure server access before starting Epic |

---

## Success Metrics

### Technical Metrics
- **Response Time**: <15 seconds average on CentOS 8
- **Query Success Rate**: >80% meaningful responses
- **System Uptime**: 95% during demo period
- **Memory Usage**: <8GB peak usage on server
- **Service Reliability**: Systemd service auto-restart working
- **Network Security**: Port 11434 properly firewalled

### Business Metrics
- **Demo Satisfaction**: >7/10 stakeholder rating
- **Use Case Coverage**: 5+ realistic scenarios
- **Source Accuracy**: Citations match retrieved content
- **Language Support**: Both Vietnamese and English working
- **Deployment Success**: Remote deployment scripts working

---

## Next Steps After PoC

Upon successful completion:
1. **Stakeholder Review**: Present results and gather feedback
2. **Business Case**: Document ROI and expansion plan
3. **Technical Roadmap**: Plan transition to Epic 2 (Internal Rollout)
4. **Resource Planning**: Secure team and infrastructure for next phase
5. **Risk Assessment**: Update risks based on PoC learnings
6. **Server Documentation**: Document CentOS 8 server configuration
7. **Performance Baseline**: Record performance metrics for comparison
8. **Team Handover**: Transfer server access and knowledge to Epic 2 team

---

**Epic Status**: Ready for Development  
**Dependencies**: CentOS 8 server access, SSH credentials, document collection  
**Blockers**: None identified

---

## Deployment Resources

### Quick Start Scripts:
- **`quick-start-us001.sh`**: Root-level quick start script
- **`scripts/deploy_us001.sh`**: Main deployment script
- **`scripts/setup_ollama_centos8.sh`**: CentOS 8 installation script
- **`scripts/remote_deploy.sh`**: Remote deployment via SSH
- **`docs/deployment/us-001-deployment-guide.md`**: Complete deployment guide

### Deployment Commands:
```bash
# Option 1: Quick deployment (from project root)
./quick-start-us001.sh

# Option 2: Direct deployment (from scripts directory)
cd scripts && ./deploy_us001.sh

# Option 3: Manual configuration
cd scripts
./remote_deploy.sh config
./remote_deploy.sh

# Option 4: Server-side installation
scp scripts/setup_ollama_centos8.sh user@server:/tmp/
ssh user@server "sudo /tmp/setup_ollama_centos8.sh"
```

### Verification Commands:
```bash
# Health check
/usr/local/bin/ollama_health_check.sh

# Service status
sudo systemctl status ollama

# Test model
ollama run mistral:7b "Test Vietnamese: Xin chào"
``` 