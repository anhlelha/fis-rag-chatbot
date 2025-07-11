# Scripts Directory - Organized Structure

## 📁 Directory Structure

```
scripts/
├── processing/          # Document processing pipeline scripts
│   ├── process_md.py           # Step 2: Process markdown files
│   ├── simple_chunk.py         # Step 4: Text chunking
│   ├── chunk_text.py           # Alternative chunking method
│   ├── extract_metadata.py     # Step 5: Metadata extraction
│   └── save_processed_data.py  # Step 6: Save processed data
├── testing/             # Testing and validation scripts
│   ├── test_pipeline.py        # Step 8: Full pipeline testing
│   └── prepare_embedding.py    # Step 7: Embedding preparation
├── deployment/          # Deployment and server setup scripts
│   ├── setup_ollama_centos8.sh     # Ollama installation
│   ├── install_with_validation.sh  # Validated installation
│   ├── deploy_us001.sh             # US-001 deployment
│   ├── remote_deploy.sh            # Remote deployment
│   ├── check_server.sh             # Server health check
│   ├── server_config.sh            # Server configuration
│   ├── install_step_by_step.sh     # Step-by-step installation
│   └── manual_install.sh           # Manual installation
├── utils/               # Utility and helper scripts
│   ├── find_md_files.py            # Find markdown files
│   ├── generate_progress_report.sh # Progress reporting
│   ├── update_dashboard.sh         # Dashboard updates
│   └── *.log files                 # Log files
└── README.md           # This file
```

## 🚀 Quick Start Commands

### US-002 Document Processing Pipeline

```bash
# Step 2: Process markdown file
python scripts/processing/process_md.py /path/to/document.md

# Step 4: Chunk the processed text
python scripts/processing/simple_chunk.py /path/to/processed_file.json

# Step 5: Extract metadata
python scripts/processing/extract_metadata.py /path/to/chunked_file.json

# Step 6: Save processed data
python scripts/processing/save_processed_data.py /path/to/metadata_file.json

# Step 7: Prepare for embedding
python scripts/testing/prepare_embedding.py /path/to/final_output_dir

# Step 8: Test full pipeline
python scripts/testing/test_pipeline.py /path/to/document.md
```

### US-001 Deployment

```bash
# Full deployment
bash scripts/deployment/deploy_us001.sh

# Server health check
bash scripts/deployment/check_server.sh

# Remote deployment
bash scripts/deployment/remote_deploy.sh
```

### Utilities

```bash
# Find markdown files
python scripts/utils/find_md_files.py

# Generate progress report
bash scripts/utils/generate_progress_report.sh

# Update dashboard
bash scripts/utils/update_dashboard.sh
```

## 📋 Script Categories

### 🔄 Processing Scripts
- **Purpose**: Document processing pipeline (US-002)
- **Input**: Markdown files
- **Output**: Embedding-ready data
- **Location**: `scripts/processing/`

### 🧪 Testing Scripts
- **Purpose**: Validation and testing
- **Input**: Processed data or raw files
- **Output**: Test results and validation reports
- **Location**: `scripts/testing/`

### 🚀 Deployment Scripts
- **Purpose**: Server setup and deployment (US-001)
- **Input**: Configuration parameters
- **Output**: Running services
- **Location**: `scripts/deployment/`

### 🛠️ Utility Scripts
- **Purpose**: Helper functions and reporting
- **Input**: Various
- **Output**: Reports, logs, utilities
- **Location**: `scripts/utils/`

## 🔧 Usage Examples

### Process a single document:
```bash
python scripts/testing/test_pipeline.py /path/to/document.md
```

### Deploy Ollama service:
```bash
bash scripts/deployment/deploy_us001.sh
```

### Find all markdown files:
```bash
python scripts/utils/find_md_files.py
```

---

**Note**: All scripts maintain backward compatibility with previous commands. The new structure provides better organization and easier maintenance. 