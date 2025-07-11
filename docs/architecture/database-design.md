# Database Design: FIS Internal AI Copilot

## Document Information
- **System**: FIS Internal AI Copilot Database Design
- **Version**: 1.0
- **Date**: December 2024
- **Architect**: Winston
- **Status**: Draft

---

## 1. Database Architecture Overview

### 1.1 Multi-Database Strategy

The AI Copilot system employs a polyglot persistence approach with specialized databases for different data types and access patterns:

```
┌─────────────────────────────────────────────────────────┐
│                Database Architecture                    │
├─────────────────────────────────────────────────────────┤
│ Primary Database \(PostgreSQL\)                          │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │   Users &   │ │ Documents   │ │   System    │       │
│ │Permissions  │ │ Metadata    │ │   Config    │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
├─────────────────────────────────────────────────────────┤
│ Vector Database \(Weaviate\)                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │  Document   │ │   Query     │ │  Semantic   │       │
│ │ Embeddings  │ │ Embeddings  │ │ Relations   │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
├─────────────────────────────────────────────────────────┤
│ Search Index \(Elasticsearch\)                          │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │  Full-Text  │ │   Faceted   │ │  Keyword    │       │
│ │   Search    │ │   Search    │ │   Search    │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
├─────────────────────────────────────────────────────────┤
│ Cache Layer \(Redis\)                                   │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │   Session   │ │    Query    │ │  Document   │       │
│ │    Cache    │ │    Cache    │ │    Cache    │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Database Responsibilities

| Database | Purpose | Technology | Use Cases |
|----------|---------|------------|-----------|
| **Primary DB** | Structured data, transactions | PostgreSQL 15 | User management, metadata, configuration |
| **Vector DB** | Semantic search, embeddings | Weaviate | Document embeddings, similarity search |
| **Search Index** | Full-text search, filtering | Elasticsearch 8.x | Keyword search, faceted filtering |
| **Cache** | Performance optimization | Redis 7.x | Session data, query results, hot data |
| **File Storage** | Binary data, documents | NFS/Object Storage | Original documents, processed content |

---

## 2. Primary Database Design \(PostgreSQL\)

### 2.1 Core Data Model

#### Entity Relationship Diagram
```
Users ──┐
        ├── UserSessions
        ├── UserRoles ──── Roles ──── RolePermissions ──── Permissions
        ├── QueryHistory
        └── UserPreferences

Documents ──┐
            ├── DocumentMetadata
            ├── DocumentVersions
            ├── DocumentPermissions ──── Users
            ├── DocumentTags ──── Tags
            ├── DocumentDepartments ──── Departments
            └── DocumentProcessingStatus

DataSources ──┐
              ├── SyncJobs
              ├── SyncLogs
              └── SourceDocuments ──── Documents

Analytics ──┐
            ├── SearchQueries
            ├── DocumentViews
            ├── UserActivity
            └── SystemMetrics
```

### 2.2 Table Schemas

#### Users Management

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    department_id UUID REFERENCES departments(id),
    employee_id VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_department ON users(department_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;

-- Departments table
CREATE TABLE departments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    parent_department_id UUID REFERENCES departments(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
```

#### Role-Based Access Control

```sql
-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL, -- documents, search, admin, etc.
    action VARCHAR(50) NOT NULL,   -- read, write, delete, etc.
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by UUID REFERENCES users(id),
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role mapping
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    PRIMARY KEY (user_id, role_id)
);
```

#### Document Management

```sql
-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA-256
    language VARCHAR(10) DEFAULT 'en',
    page_count INTEGER,
    word_count INTEGER,
    
    -- Source information
    source_type VARCHAR(50) NOT NULL, -- sharepoint, google_drive, file_server
    source_id VARCHAR(255) NOT NULL,
    source_path TEXT NOT NULL,
    source_last_modified TIMESTAMP,
    
    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    processing_error TEXT,
    
    -- Metadata
    author VARCHAR(255),
    created_by UUID REFERENCES users(id),
    department_id UUID REFERENCES departments(id),
    classification VARCHAR(50) DEFAULT 'internal', -- public, internal, confidential, secret
    
    -- Timestamps
    indexed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT documents_file_size_positive CHECK (file_size_bytes > 0),
    CONSTRAINT documents_processing_status_valid CHECK (
        processing_status IN ('pending', 'processing', 'completed', 'failed', 'skipped')
    )
);

-- Indexes
CREATE INDEX idx_documents_source ON documents(source_type, source_id);
CREATE INDEX idx_documents_status ON documents(processing_status);
CREATE INDEX idx_documents_department ON documents(department_id);
CREATE INDEX idx_documents_classification ON documents(classification);
CREATE INDEX idx_documents_hash ON documents(file_hash);
CREATE INDEX idx_documents_created ON documents(created_at);

-- Document metadata (extensible key-value pairs)
CREATE TABLE document_metadata (
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    key VARCHAR(100) NOT NULL,
    value TEXT,
    value_type VARCHAR(20) DEFAULT 'string', -- string, number, date, boolean
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (document_id, key)
);

CREATE INDEX idx_document_metadata_key ON document_metadata(key);

-- Document versions
CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    source_last_modified TIMESTAMP NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(document_id, version_number)
);
```

#### Tags and Categories

```sql
-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7), -- hex color code
    description TEXT,
    is_system_tag BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document-Tag mapping
CREATE TABLE document_tags (
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (document_id, tag_id)
);

-- Categories (hierarchical)
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    parent_category_id UUID REFERENCES categories(id),
    path TEXT, -- materialized path for hierarchy
    level INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_parent ON categories(parent_category_id);
CREATE INDEX idx_categories_path ON categories(path);

-- Document-Category mapping
CREATE TABLE document_categories (
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (document_id, category_id)
);
```

#### Data Source Management

```sql
-- Data sources configuration
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL, -- sharepoint, google_drive, file_server
    configuration JSONB NOT NULL, -- source-specific config
    is_enabled BOOLEAN DEFAULT true,
    sync_schedule VARCHAR(100), -- cron expression
    last_sync_at TIMESTAMP,
    last_successful_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT data_sources_type_valid CHECK (
        type IN ('sharepoint', 'google_drive', 'file_server', 'onedrive')
    )
);

-- Sync jobs tracking
CREATE TABLE sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_source_id UUID NOT NULL REFERENCES data_sources(id),
    job_type VARCHAR(50) NOT NULL, -- full_sync, incremental_sync
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed, cancelled
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    documents_processed INTEGER DEFAULT 0,
    documents_added INTEGER DEFAULT 0,
    documents_updated INTEGER DEFAULT 0,
    documents_deleted INTEGER DEFAULT 0,
    error_message TEXT,
    
    CONSTRAINT sync_jobs_type_valid CHECK (
        job_type IN ('full_sync', 'incremental_sync', 'validation_sync')
    )
);

CREATE INDEX idx_sync_jobs_source ON sync_jobs(data_source_id);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status);
CREATE INDEX idx_sync_jobs_started ON sync_jobs(started_at);
```

### 2.3 Partitioning Strategy

#### Time-based Partitioning for Analytics Tables

```sql
-- Partitioned table for search queries
CREATE TABLE search_queries (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50) DEFAULT 'natural_language',
    filters JSONB,
    results_count INTEGER,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Monthly partitions
CREATE TABLE search_queries_2024_12 PARTITION OF search_queries
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

CREATE TABLE search_queries_2025_01 PARTITION OF search_queries
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Document views tracking
CREATE TABLE document_views (
    id UUID DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id),
    user_id UUID NOT NULL REFERENCES users(id),
    view_type VARCHAR(50) DEFAULT 'search_result', -- search_result, direct_access, download
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);
```

---

## 3. Vector Database Design \(Weaviate\)

### 3.1 Schema Configuration

#### Document Embeddings Schema

```json
{
  "class": "DocumentEmbedding",
  "description": "Document embeddings for semantic search",
  "vectorizer": "text2vec-transformers",
  "vectorIndexType": "hnsw",
  "vectorIndexConfig": {
    "ef": 64,
    "efConstruction": 128,
    "maxConnections": 32,
    "cleanupIntervalSeconds": 300
  },
  "properties": [
    {
      "name": "documentId",
      "dataType": ["string"],
      "description": "Document ID from primary database",
      "indexInverted": true
    },
    {
      "name": "chunkId",
      "dataType": ["string"],
      "description": "Unique identifier for document chunk",
      "indexInverted": true
    },
    {
      "name": "title",
      "dataType": ["text"],
      "description": "Document title"
    },
    {
      "name": "content",
      "dataType": ["text"],
      "description": "Document chunk content"
    },
    {
      "name": "contentType",
      "dataType": ["string"],
      "description": "Type of content: title, paragraph, table, list"
    },
    {
      "name": "pageNumber",
      "dataType": ["int"],
      "description": "Page number in original document"
    },
    {
      "name": "chunkIndex",
      "dataType": ["int"],
      "description": "Chunk sequence in document"
    },
    {
      "name": "language",
      "dataType": ["string"],
      "description": "Content language (en, vi)"
    },
    {
      "name": "department",
      "dataType": ["string"],
      "description": "Document department",
      "indexInverted": true
    },
    {
      "name": "sourceType",
      "dataType": ["string"],
      "description": "Source system type",
      "indexInverted": true
    },
    {
      "name": "classification",
      "dataType": ["string"],
      "description": "Security classification",
      "indexInverted": true
    },
    {
      "name": "tags",
      "dataType": ["string[]"],
      "description": "Document tags",
      "indexInverted": true
    },
    {
      "name": "lastModified",
      "dataType": ["date"],
      "description": "Document last modification date"
    },
    {
      "name": "embedding",
      "dataType": ["number[]"],
      "description": "Vector embedding"
    }
  ]
}
```

#### Query Embeddings Schema

```json
{
  "class": "QueryEmbedding",
  "description": "User query embeddings for query expansion and analysis",
  "vectorizer": "text2vec-transformers",
  "properties": [
    {
      "name": "queryId",
      "dataType": ["string"],
      "description": "Query ID from analytics",
      "indexInverted": true
    },
    {
      "name": "queryText",
      "dataType": ["text"],
      "description": "Original query text"
    },
    {
      "name": "normalizedQuery",
      "dataType": ["text"],
      "description": "Normalized and processed query"
    },
    {
      "name": "language",
      "dataType": ["string"],
      "description": "Query language"
    },
    {
      "name": "userId",
      "dataType": ["string"],
      "description": "User who made the query"
    },
    {
      "name": "department",
      "dataType": ["string"],
      "description": "User department"
    },
    {
      "name": "createdAt",
      "dataType": ["date"],
      "description": "Query timestamp"
    }
  ]
}
```

### 3.2 Vector Operations

#### Similarity Search Configuration

```python
# Semantic search with filters
search_query = {
    "query": {
        "vector": query_embedding,
        "filters": {
            "department": ["HR", "Engineering"],
            "classification": ["internal", "public"],
            "lastModified": {
                "gte": "2024-01-01T00:00:00Z"
            }
        }
    },
    "limit": 50,
    "offset": 0,
    "certainty": 0.7,  # Minimum similarity threshold
    "additional": ["distance", "certainty"]
}
```

#### Hybrid Search Implementation

```python
# Combine vector and keyword search
hybrid_query = {
    "query": {
        "hybrid": {
            "vector": query_embedding,
            "keyword": "vacation policy",
            "alpha": 0.7  # Weight: 0.7 semantic + 0.3 keyword
        },
        "filters": {
            "sourceType": ["sharepoint", "google_drive"]
        }
    },
    "limit": 20
}
```

---

## 4. Search Index Design \(Elasticsearch\)

### 4.1 Index Mapping

#### Documents Index

```json
{
  "mappings": {
    "properties": {
      "document_id": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword"
          },
          "suggest": {
            "type": "completion",
            "analyzer": "simple"
          }
        }
      },
      "content": {
        "type": "text",
        "analyzer": "multilingual_analyzer"
      },
      "content_chunks": {
        "type": "nested",
        "properties": {
          "chunk_id": {"type": "keyword"},
          "content": {"type": "text"},
          "page_number": {"type": "integer"},
          "chunk_index": {"type": "integer"}
        }
      },
      "author": {
        "type": "text",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "department": {
        "type": "keyword"
      },
      "source_type": {
        "type": "keyword"
      },
      "source_path": {
        "type": "keyword"
      },
      "file_type": {
        "type": "keyword"
      },
      "classification": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "language": {
        "type": "keyword"
      },
      "file_size": {
        "type": "long"
      },
      "page_count": {
        "type": "integer"
      },
      "word_count": {
        "type": "integer"
      },
      "created_at": {
        "type": "date"
      },
      "updated_at": {
        "type": "date"
      },
      "last_modified": {
        "type": "date"
      },
      "indexed_at": {
        "type": "date"
      }
    }
  },
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "multilingual_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "asciifolding",
            "vietnamese_stop",
            "english_stop",
            "vietnamese_stemmer"
          ]
        }
      },
      "filter": {
        "vietnamese_stop": {
          "type": "stop",
          "stopwords": ["và", "của", "với", "trong", "trên", "dưới"]
        },
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        },
        "vietnamese_stemmer": {
          "type": "stemmer",
          "language": "light_vietnamese"
        }
      }
    }
  }
}
```

### 4.2 Search Templates

#### Faceted Search Template

```json
{
  "script": {
    "lang": "mustache",
    "source": {
      "query": {
        "bool": {
          "must": [
            {
              "multi_match": {
                "query": "{{query_text}}",
                "fields": ["title^3", "content^1", "author^2"],
                "type": "best_fields",
                "fuzziness": "AUTO"
              }
            }
          ],
          "filter": [
            {{#departments}}
            {
              "terms": {
                "department": {{departments}}
              }
            },
            {{/departments}}
            {{#date_range}}
            {
              "range": {
                "last_modified": {
                  "gte": "{{date_range.start}}",
                  "lte": "{{date_range.end}}"
                }
              }
            },
            {{/date_range}}
            {{#file_types}}
            {
              "terms": {
                "file_type": {{file_types}}
              }
            }
            {{/file_types}}
          ]
        }
      },
      "aggs": {
        "departments": {
          "terms": {
            "field": "department",
            "size": 20
          }
        },
        "file_types": {
          "terms": {
            "field": "file_type",
            "size": 10
          }
        },
        "tags": {
          "terms": {
            "field": "tags",
            "size": 50
          }
        },
        "date_histogram": {
          "date_histogram": {
            "field": "last_modified",
            "calendar_interval": "month"
          }
        }
      },
      "highlight": {
        "fields": {
          "title": {},
          "content": {
            "fragment_size": 150,
            "number_of_fragments": 3
          }
        }
      },
      "sort": [
        {"_score": {"order": "desc"}},
        {"last_modified": {"order": "desc"}}
      ]
    }
  }
}
```

---

## 5. Cache Design \(Redis\)

### 5.1 Cache Structure

#### Cache Key Patterns

```
# User sessions
session:{session_token} → {user_data, expires_at}

# Query results cache
query:{query_hash}:{user_id}:{filters_hash} → {search_results, ttl: 1h}

# Document metadata cache
doc:{document_id} → {metadata, ttl: 6h}

# User permissions cache
perms:{user_id} → {permissions_list, ttl: 15m}

# Popular queries cache
popular:queries:{department}:{timeframe} → {query_list, ttl: 24h}

# System configuration cache
config:{key} → {value, ttl: 1h}

# Analytics cache
analytics:{type}:{period}:{params_hash} → {data, ttl: 30m}
```

### 5.2 Cache Configuration

```redis
# Memory optimization
maxmemory 8gb
maxmemory-policy allkeys-lru

# Persistence (for important data)
save 900 1     # Save if at least 1 key changed in 900 seconds
save 300 10    # Save if at least 10 keys changed in 300 seconds  
save 60 10000  # Save if at least 10000 keys changed in 60 seconds

# Redis Cluster configuration
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
```

#### Cache Management Strategies

```python
# Cache warming for popular queries
def warm_cache():
    popular_queries = get_popular_queries(last_7_days=True)
    for query in popular_queries:
        departments = get_user_departments_for_query(query)
        for dept in departments:
            cache_key = f"query:{hash(query)}:dept_{dept}"
            if not redis.exists(cache_key):
                results = execute_search(query, department_filter=dept)
                redis.setex(cache_key, 3600, json.dumps(results))

# Cache invalidation on document updates
def invalidate_document_cache(document_id):
    # Invalidate document metadata
    redis.delete(f"doc:{document_id}")
    
    # Invalidate related query caches
    pattern = f"query:*"
    for key in redis.scan_iter(match=pattern):
        # Check if cached results contain this document
        cached_data = redis.get(key)
        if document_id in cached_data:
            redis.delete(key)
```

---

## 6. Data Migration & Seeding

### 6.1 Initial Data Setup

#### Default Roles and Permissions

```sql
-- Insert default departments
INSERT INTO departments (id, name, code) VALUES
('00000000-0000-0000-0000-000000000001', 'Human Resources', 'HR'),
('00000000-0000-0000-0000-000000000002', 'Engineering', 'ENG'),
('00000000-0000-0000-0000-000000000003', 'Finance', 'FIN'),
('00000000-0000-0000-0000-000000000004', 'Legal', 'LEG'),
('00000000-0000-0000-0000-000000000005', 'Administration', 'ADM');

-- Insert default roles
INSERT INTO roles (id, name, description, is_system_role) VALUES
('10000000-0000-0000-0000-000000000001', 'Super Admin', 'Full system access', true),
('10000000-0000-0000-0000-000000000002', 'Department Admin', 'Department-level administration', true),
('10000000-0000-0000-0000-000000000003', 'Power User', 'Advanced search and analytics access', true),
('10000000-0000-0000-0000-000000000004', 'Regular User', 'Standard document search access', true),
('10000000-0000-0000-0000-000000000005', 'Read Only', 'View-only access', true);

-- Insert default permissions
INSERT INTO permissions (name, resource, action, description) VALUES
('documents.read', 'documents', 'read', 'View documents'),
('documents.download', 'documents', 'download', 'Download documents'),
('documents.upload', 'documents', 'upload', 'Upload new documents'),
('documents.delete', 'documents', 'delete', 'Delete documents'),
('search.basic', 'search', 'basic', 'Basic search functionality'),
('search.advanced', 'search', 'advanced', 'Advanced search features'),
('analytics.view', 'analytics', 'view', 'View analytics dashboards'),
('admin.users', 'admin', 'users', 'User management'),
('admin.system', 'admin', 'system', 'System configuration'),
('admin.datasources', 'admin', 'datasources', 'Data source management');
```

### 6.2 Data Migration Scripts

#### Document Import Script

```python
def migrate_documents_from_source(source_config):
    """
    Migrate documents from external source to AI Copilot system
    """
    source_type = source_config['type']
    batch_size = 100
    
    # Initialize connectors
    if source_type == 'sharepoint':
        connector = SharePointConnector(source_config)
    elif source_type == 'google_drive':
        connector = GoogleDriveConnector(source_config)
    
    # Process documents in batches
    offset = 0
    while True:
        documents = connector.get_documents(limit=batch_size, offset=offset)
        if not documents:
            break
            
        for doc in documents:
            # Insert into PostgreSQL
            doc_id = insert_document_metadata(doc)
            
            # Process and extract content
            content = extract_document_content(doc['file_path'])
            
            # Generate embeddings
            embeddings = generate_embeddings(content)
            
            # Store in Weaviate
            store_document_embeddings(doc_id, embeddings)
            
            # Index in Elasticsearch
            index_document_content(doc_id, content, doc['metadata'])
            
        offset += batch_size
        
    logger.info(f"Migration completed: {offset} documents processed")
```

---

## 7. Performance Optimization

### 7.1 Database Optimization

#### PostgreSQL Optimization

```sql
-- Connection pooling configuration
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

-- Query optimization
CREATE STATISTICS documents_multi_stats ON source_type, department_id, classification FROM documents;

-- Partial indexes for common queries
CREATE INDEX idx_documents_active_recent 
ON documents (created_at DESC) 
WHERE processing_status = 'completed' AND indexed_at IS NOT NULL;

-- Materialized views for analytics
CREATE MATERIALIZED VIEW mv_popular_documents AS
SELECT 
    d.id,
    d.title,
    d.department_id,
    COUNT(dv.id) as view_count,
    COUNT(DISTINCT dv.user_id) as unique_viewers
FROM documents d
LEFT JOIN document_views dv ON d.id = dv.document_id
WHERE dv.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY d.id, d.title, d.department_id
ORDER BY view_count DESC;

-- Refresh schedule
SELECT cron.schedule('refresh-popular-docs', '0 2 * * *', 'REFRESH MATERIALIZED VIEW mv_popular_documents;');
```

#### Weaviate Optimization

```python
# Batch operations for better performance
def batch_insert_embeddings(embeddings_data):
    client = weaviate.Client("http://weaviate:8080")
    
    with client.batch(
        batch_size=100,
        num_workers=4,
        dynamic=True
    ) as batch:
        for data in embeddings_data:
            batch.add_data_object(
                data_object=data,
                class_name="DocumentEmbedding"
            )
```

### 7.2 Query Optimization

#### Smart Caching Strategy

```python
def get_cached_search_results(query_hash, user_id, filters_hash):
    cache_key = f"query:{query_hash}:{user_id}:{filters_hash}"
    
    # Try L1 cache (Redis)
    cached_result = redis.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    
    # Try L2 cache (PostgreSQL materialized view)
    mv_result = get_from_materialized_view(query_hash)
    if mv_result and is_fresh_enough(mv_result):
        # Store in L1 cache
        redis.setex(cache_key, 1800, json.dumps(mv_result))
        return mv_result
    
    # Cache miss - execute fresh search
    return None
```

---

## 8. Backup & Recovery

### 8.1 Backup Strategy

#### PostgreSQL Backup

```bash
#!/bin/bash
# Daily backup script

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="ai_copilot"

# Full backup
pg_dump -h localhost -U postgres -d $DB_NAME \
    --format=custom --compress=9 --verbose \
    --file="$BACKUP_DIR/full_backup_$DATE.dump"

# Incremental backup using WAL archiving
# (configured in postgresql.conf)
archive_mode = on
archive_command = 'rsync %p /backups/postgresql/wal_archive/%f'
```

#### Vector Database Backup

```python
def backup_weaviate_data():
    """
    Backup Weaviate vector data
    """
    client = weaviate.Client("http://weaviate:8080")
    
    # Export all classes
    classes = ['DocumentEmbedding', 'QueryEmbedding']
    backup_data = {}
    
    for class_name in classes:
        objects = client.data_object.get(
            class_name=class_name,
            limit=10000,  # Adjust based on data size
            additional=["vector"]
        )
        backup_data[class_name] = objects['objects']
    
    # Save to S3 or local storage
    backup_file = f"weaviate_backup_{datetime.now().isoformat()}.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
```

### 8.2 Disaster Recovery

#### Recovery Procedures

```sql
-- Point-in-time recovery for PostgreSQL
# 1. Restore base backup
pg_restore -h localhost -U postgres -d ai_copilot_recovery /backups/full_backup_20241201.dump

# 2. Apply WAL files up to specific point
recovery_target_time = '2024-12-01 14:30:00'
recovery_target_action = 'promote'
```

---

## 9. Monitoring & Alerting

### 9.1 Database Monitoring

#### PostgreSQL Monitoring Queries

```sql
-- Long running queries
SELECT 
    pid,
    user,
    query_start,
    state,
    query
FROM pg_stat_activity 
WHERE state != 'idle' 
AND query_start < NOW() - INTERVAL '5 minutes';

-- Table sizes and growth
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;

-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

#### Performance Alerts

```python
# Database monitoring alerts
def check_database_health():
    alerts = []
    
    # Connection count alert
    conn_count = get_active_connections()
    if conn_count > 150:  # 75% of max_connections
        alerts.append({
            'level': 'warning',
            'message': f'High connection count: {conn_count}/200'
        })
    
    # Slow query alert
    slow_queries = get_slow_queries(threshold_seconds=10)
    if len(slow_queries) > 5:
        alerts.append({
            'level': 'critical',
            'message': f'{len(slow_queries)} slow queries detected'
        })
    
    # Disk space alert
    disk_usage = get_disk_usage()
    if disk_usage > 85:
        alerts.append({
            'level': 'critical',
            'message': f'High disk usage: {disk_usage}%'
        })
    
    return alerts
```

---

## 10. Security Considerations

### 10.1 Data Encryption

#### Transparent Data Encryption

```sql
-- PostgreSQL TDE configuration
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'

# Column-level encryption for sensitive data
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive configuration data
INSERT INTO data_sources (name, type, configuration) VALUES (
    'HR SharePoint',
    'sharepoint',
    pgp_sym_encrypt(
        '{"client_id": "secret_id", "client_secret": "secret_value"}',
        'encryption_key'
    )
);
```

### 10.2 Access Control

#### Row Level Security

```sql
-- Enable RLS on sensitive tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policy for department-based access
CREATE POLICY documents_department_policy ON documents
    FOR SELECT
    TO authenticated_users
    USING (
        department_id IN (
            SELECT department_id 
            FROM user_department_access 
            WHERE user_id = current_user_id()
        )
        OR classification = 'public'
    );

-- Function to get current user departments
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
    SELECT user_id FROM user_sessions 
    WHERE session_token = current_setting('app.session_token')
    AND expires_at > NOW()
    LIMIT 1;
$$ LANGUAGE SQL SECURITY DEFINER;
```

### 10.3 Audit Logging

#### Comprehensive Audit Trail

```sql
-- Audit log table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id, action, resource_type, resource_id,
        old_values, new_values, ip_address, session_id
    ) VALUES (
        current_user_id(),
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id::text, OLD.id::text),
        CASE WHEN TG_OP = 'DELETE' THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
        inet_client_addr(),
        current_setting('app.session_id', true)
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply audit trigger to sensitive tables
CREATE TRIGGER documents_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON documents
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

---

**Document Status**: Draft v1.0  
**Next Review**: Post-database implementation  
**Dependencies**: System Architecture, API Specifications 