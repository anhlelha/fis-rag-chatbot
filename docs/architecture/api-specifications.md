# API Specifications: FIS Internal AI Copilot

## Document Information
- **System**: FIS Internal AI Copilot APIs
- **Version**: 1.0
- **Date**: December 2024
- **Architect**: Winston
- **Status**: Draft

---

## 1. API Overview

### 1.1 API Architecture
The AI Copilot system exposes RESTful APIs following OpenAPI 3.0 specifications with comprehensive authentication, rate limiting, and monitoring capabilities.

### 1.2 Base Configuration
- **Base URL**: `https://ai-copilot.fis.internal/api/v1`
- **Protocol**: HTTPS only \(TLS 1.3\)
- **Content Type**: `application/json`
- **Authentication**: Bearer token \(JWT\)
- **Rate Limiting**: 1000 requests per hour per user

---

## 2. Authentication APIs

### 2.1 SSO Authentication

#### Login Endpoint
```http
POST /auth/login
Content-Type: application/json

{
  "sso_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "remember_me": true
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "user": {
      "id": "user123",
      "email": "user@fis.com",
      "name": "John Doe",
      "department": "Engineering",
      "roles": ["user", "viewer"]
    }
  }
}
```

#### Token Refresh
```http
POST /auth/refresh
Authorization: Bearer {refresh_token}

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Logout
```http
POST /auth/logout
Authorization: Bearer {access_token}
```

---

## 3. Search APIs

### 3.1 Main Search Endpoint

#### Natural Language Search
```http
POST /search
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "query": "What is the remote work policy for engineers?",
  "filters": {
    "departments": ["HR", "Engineering"],
    "document_types": ["pdf", "docx", "txt"],
    "date_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-12-31T23:59:59Z"
    },
    "sources": ["sharepoint", "google_drive"],
    "tags": ["policy", "remote-work"]
  },
  "options": {
    "max_results": 10,
    "include_summary": true,
    "include_snippets": true,
    "highlight_terms": true,
    "response_language": "vi"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "query_id": "qry_789abc123",
    "total_results": 25,
    "processing_time_ms": 1234,
    "results": [
      {
        "document_id": "doc_456def789",
        "title": "Remote Work Policy 2024",
        "summary": "Updated remote work policy allowing flexible arrangements...",
        "relevance_score": 0.95,
        "source": {
          "system": "sharepoint",
          "url": "https://fis.sharepoint.com/sites/hr/policies/remote-work.pdf",
          "last_modified": "2024-11-15T10:30:00Z",
          "author": "HR Department",
          "department": "HR"
        },
        "snippets": [
          {
            "text": "Engineers may work remotely up to 3 days per week...",
            "page": 2,
            "context": "Section 2.1: Engineering Department Guidelines"
          }
        ],
        "confidence": 0.92
      }
    ],
    "suggested_queries": [
      "What are the equipment requirements for remote work?",
      "How to request remote work approval?"
    ]
  }
}
```

### 3.2 Advanced Search Features

#### Semantic Search
```http
POST /search/semantic
{
  "query": "How to submit expense reports?",
  "similarity_threshold": 0.8,
  "max_results": 20
}
```

#### Keyword Search
```http
POST /search/keyword
{
  "query": "expense report submission process",
  "exact_match": false,
  "fuzzy_matching": true
}
```

#### Hybrid Search
```http
POST /search/hybrid
{
  "query": "vacation policy",
  "semantic_weight": 0.7,
  "keyword_weight": 0.3,
  "boost_recent": true
}
```

---

## 4. Document APIs

### 4.1 Document Retrieval

#### Get Document Details
```http
GET /documents/{document_id}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "doc_456def789",
    "title": "Remote Work Policy 2024",
    "type": "pdf",
    "size_bytes": 2048000,
    "pages": 15,
    "language": "en",
    "source": {
      "system": "sharepoint",
      "path": "/sites/hr/policies/remote-work.pdf",
      "last_modified": "2024-11-15T10:30:00Z",
      "author": "HR Department",
      "version": "1.2"
    },
    "metadata": {
      "department": "HR",
      "category": "policy",
      "tags": ["remote-work", "policy", "2024"],
      "classification": "internal"
    },
    "permissions": {
      "can_view": true,
      "can_download": true,
      "can_share": false
    },
    "processing_status": "completed",
    "indexed_at": "2024-11-15T11:00:00Z"
  }
}
```

#### Get Document Content
```http
GET /documents/{document_id}/content
Authorization: Bearer {access_token}
Accept: application/json | application/pdf | text/plain
```

#### Download Document
```http
GET /documents/{document_id}/download
Authorization: Bearer {access_token}
```

### 4.2 Document Management

#### Upload Document
```http
POST /documents/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: {binary_data}
metadata: {
  "title": "New Policy Document",
  "department": "HR",
  "tags": ["policy", "new"],
  "classification": "internal"
}
```

#### Update Document Metadata
```http
PUT /documents/{document_id}/metadata
{
  "title": "Updated Policy Document",
  "tags": ["policy", "updated", "2024"],
  "department": "HR"
}
```

---

## 5. Analytics APIs

### 5.1 Usage Analytics

#### Search Analytics
```http
GET /analytics/search
Authorization: Bearer {access_token}
Query Parameters:
- start_date: 2024-11-01
- end_date: 2024-11-30
- granularity: daily|weekly|monthly
- department: HR|Engineering|Finance
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "period": {
      "start": "2024-11-01T00:00:00Z",
      "end": "2024-11-30T23:59:59Z"
    },
    "metrics": {
      "total_searches": 15420,
      "unique_users": 1205,
      "average_response_time_ms": 2150,
      "success_rate": 0.89,
      "top_queries": [
        {
          "query": "vacation policy",
          "count": 234,
          "success_rate": 0.95
        }
      ]
    },
    "trends": [
      {
        "date": "2024-11-01",
        "searches": 512,
        "users": 89
      }
    ]
  }
}
```

#### Document Analytics
```http
GET /analytics/documents
Query Parameters:
- sort_by: views|downloads|searches
- period: 7d|30d|90d
- limit: 50
```

#### User Activity Analytics
```http
GET /analytics/users
Query Parameters:
- user_id: user123
- include_history: true
- limit: 100
```

---

## 6. Administration APIs

### 6.1 System Configuration

#### Get System Status
```http
GET /admin/status
Authorization: Bearer {admin_token}
```

**Response:**
```json
{
  "status": "healthy",
  "data": {
    "version": "1.0.0",
    "uptime_seconds": 2592000,
    "services": {
      "api_gateway": "healthy",
      "search_engine": "healthy", 
      "vector_database": "healthy",
      "document_processor": "degraded",
      "auth_service": "healthy"
    },
    "performance": {
      "avg_response_time_ms": 1850,
      "requests_per_minute": 450,
      "error_rate": 0.02
    },
    "resources": {
      "cpu_usage": 0.65,
      "memory_usage": 0.78,
      "disk_usage": 0.45,
      "gpu_usage": 0.82
    }
  }
}
```

#### Update Configuration
```http
PUT /admin/config
{
  "search": {
    "max_results_default": 10,
    "timeout_seconds": 30,
    "cache_ttl_minutes": 60
  },
  "security": {
    "session_timeout_minutes": 480,
    "max_login_attempts": 5
  }
}
```

### 6.2 Data Source Management

#### List Data Sources
```http
GET /admin/datasources
```

#### Add Data Source
```http
POST /admin/datasources
{
  "type": "sharepoint",
  "name": "HR SharePoint Site",
  "config": {
    "site_url": "https://fis.sharepoint.com/sites/hr",
    "client_id": "app-client-id",
    "tenant_id": "tenant-id"
  },
  "sync_schedule": "0 */4 * * *",
  "enabled": true
}
```

#### Sync Data Source
```http
POST /admin/datasources/{source_id}/sync
{
  "full_sync": true,
  "force": false
}
```

---

## 7. WebSocket APIs

### 7.1 Real-time Search

#### WebSocket Connection
```javascript
const ws = new WebSocket('wss://ai-copilot.fis.internal/ws/search');

ws.onopen = function() {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  }));
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  // Handle real-time search results
};
```

#### Real-time Query
```javascript
ws.send(JSON.stringify({
  type: 'search',
  query: 'vacation policy',
  stream: true
}));
```

**Response Stream:**
```json
{"type": "search_start", "query_id": "qry_123"}
{"type": "result", "data": {...}, "partial": true}
{"type": "result", "data": {...}, "partial": true}
{"type": "search_complete", "total_results": 15}
```

---

## 8. Error Handling

### 8.1 Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query parameter is required",
    "details": {
      "field": "query",
      "value": "",
      "constraint": "min_length_3"
    },
    "request_id": "req_789xyz456",
    "timestamp": "2024-12-01T10:30:00Z"
  }
}
```

### 8.2 Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request |
| `UNAUTHORIZED` | 401 | Invalid or missing token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `SEARCH_TIMEOUT` | 408 | Search query timeout |
| `PROCESSING_ERROR` | 422 | Document processing failed |
| `SERVICE_UNAVAILABLE` | 503 | System maintenance |

---

## 9. Rate Limiting

### 9.1 Rate Limit Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Resource: search
```

### 9.2 Rate Limit Tiers

| User Type | Requests/Hour | Burst Limit |
|-----------|---------------|-------------|
| Regular User | 1,000 | 100 |
| Power User | 5,000 | 500 |
| Admin | 10,000 | 1,000 |
| Service Account | 50,000 | 5,000 |

---

## 10. API Versioning

### 10.1 Versioning Strategy
- **URL Path Versioning**: `/api/v1/`, `/api/v2/`
- **Backward Compatibility**: 2 versions supported
- **Deprecation Notice**: 6 months advance notice
- **Migration Guide**: Detailed migration documentation

### 10.2 Version Headers
```http
GET /api/v1/search
API-Version: 1.0
Accept: application/vnd.fis.copilot.v1+json
```

---

## 11. Security Specifications

### 11.1 API Security

#### Authentication:
- **JWT Tokens**: RS256 signing algorithm
- **Token Expiry**: 1 hour access, 24 hour refresh
- **Scope-based Access**: Granular permission system
- **Rate Limiting**: Per-user and per-endpoint limits

#### Input Validation:
- **Request Sanitization**: XSS and injection prevention
- **Schema Validation**: JSON schema validation
- **File Upload Security**: Type and size restrictions
- **Query Limits**: Maximum query length and complexity

### 11.2 CORS Configuration

```json
{
  "allowed_origins": [
    "https://ai-copilot.fis.internal",
    "https://admin.fis.internal"
  ],
  "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
  "allowed_headers": ["Authorization", "Content-Type"],
  "max_age": 86400
}
```

---

## 12. API Documentation

### 12.1 OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: FIS Internal AI Copilot API
  version: 1.0.0
  description: RESTful API for internal document search and retrieval
  contact:
    name: Architecture Team
    email: architecture@fis.com
servers:
  - url: https://ai-copilot.fis.internal/api/v1
    description: Production server
paths:
  /search:
    post:
      summary: Search documents using natural language
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchRequest'
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResponse'
```

### 12.2 Interactive Documentation
- **Swagger UI**: Available at `/api/docs`
- **Postman Collection**: Downloadable collection
- **Code Examples**: Multiple language samples
- **Testing Interface**: Built-in API testing

---

**Document Status**: Draft v1.0  
**Next Review**: Post-API implementation  
**Integration**: OpenAPI 3.0 specification included 