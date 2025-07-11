# Deployment Guide: FIS Internal AI Copilot

## Document Information
- **System**: FIS Internal AI Copilot Deployment
- **Version**: 1.0
- **Date**: December 2024
- **Architect**: Winston
- **Status**: Draft

---

## 1. Infrastructure Requirements

### 1.1 Hardware Specifications

#### Production Environment
```
┌─────────────────────────────────────────────────────────┐
│                Production Infrastructure                │
├─────────────────────────────────────────────────────────┤
│ Load Balancer Tier (2 nodes)                          │
│ • CPU: 4 vCPU each                                    │
│ • RAM: 8GB each                                       │
│ • Storage: 100GB SSD each                             │
│ • Network: 1Gbps                                      │
├─────────────────────────────────────────────────────────┤
│ Application Tier (3 nodes)                            │
│ • CPU: 8 vCPU each                                    │
│ • RAM: 32GB each                                      │
│ • Storage: 500GB SSD each                             │
│ • Network: 1Gbps                                      │
├─────────────────────────────────────────────────────────┤
│ AI/ML Tier (2 nodes)                                  │
│ • CPU: 16 vCPU each                                   │
│ • RAM: 64GB each                                      │
│ • GPU: 2x RTX 4090 or A100                           │
│ • Storage: 1TB NVMe SSD each                          │
│ • Network: 10Gbps                                     │
├─────────────────────────────────────────────────────────┤
│ Database Tier (3 nodes)                               │
│ • CPU: 16 vCPU each                                   │
│ • RAM: 128GB each                                     │
│ • Storage: 4TB NVMe SSD each                          │
│ • Network: 10Gbps                                     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Network Architecture

```
Internet ──► Firewall ──► Load Balancer ──► DMZ
                              │
                              ▼
Corporate Network ──► Application Tier ──► Internal Network
                              │
                              ▼
                        Database Tier ──► Secure Zone
```

---

## 2. Container Deployment

### 2.1 Docker Compose Configuration

#### Production Stack
```yaml
version: '3.8'

services:
  # API Gateway
  kong:
    image: kong:3.4
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_DATABASE: kong
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_PG_PASSWORD}
    ports:
      - "8000:8000"
      - "8001:8001"
    depends_on:
      - postgres

  # Application Services
  api-server:
    image: fis/ai-copilot-api:${VERSION}
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/ai_copilot
      REDIS_URL: redis://redis:6379
      WEAVIATE_URL: http://weaviate:8080
      ELASTICSEARCH_URL: http://elasticsearch:9200
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
          cpus: '2'
    depends_on:
      - postgres
      - redis
      - weaviate
      - elasticsearch

  # RAG Engine
  rag-engine:
    image: fis/ai-copilot-rag:${VERSION}
    environment:
      MODEL_PATH: /models/llama-2-7b
      EMBEDDING_MODEL: sentence-transformers/all-MiniLM-L6-v2
    volumes:
      - models:/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Vector Database
  weaviate:
    image: semitechnologies/weaviate:1.22.4
    ports:
      - "8080:8080"
    environment:
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
    volumes:
      - weaviate_data:/var/lib/weaviate

  # Search Engine
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    deploy:
      resources:
        limits:
          memory: 8G

  # Primary Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_copilot
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  # Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  weaviate_data:
  elasticsearch_data:
  redis_data:
  models:
```

### 2.2 Kubernetes Deployment

#### Application Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-copilot-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-copilot-api
  template:
    metadata:
      labels:
        app: ai-copilot-api
    spec:
      containers:
      - name: api
        image: fis/ai-copilot-api:1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 3. Security Configuration

### 3.1 SSL/TLS Setup

#### Certificate Configuration
```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ai-copilot.key \
  -out ai-copilot.crt \
  -subj "/C=VN/ST=HCM/L=HoChiMinh/O=FIS/CN=ai-copilot.fis.internal"

# Configure nginx SSL
server {
    listen 443 ssl http2;
    server_name ai-copilot.fis.internal;
    
    ssl_certificate /etc/ssl/certs/ai-copilot.crt;
    ssl_certificate_key /etc/ssl/private/ai-copilot.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    
    location / {
        proxy_pass http://app-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3.2 Firewall Rules

```bash
# Basic firewall configuration
# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow internal communication
iptables -A INPUT -s 10.0.0.0/8 -j ACCEPT

# Database access (internal only)
iptables -A INPUT -p tcp --dport 5432 -s 10.0.1.0/24 -j ACCEPT

# Drop all other incoming traffic
iptables -A INPUT -j DROP
```

---

## 4. Environment Configuration

### 4.1 Environment Variables

#### Production Environment
```bash
# Database Configuration
DATABASE_HOST=postgres-cluster.internal
DATABASE_PORT=5432
DATABASE_NAME=ai_copilot
DATABASE_USER=ai_copilot_app
DATABASE_PASSWORD=${DATABASE_PASSWORD}
DATABASE_SSL_MODE=require

# Redis Configuration
REDIS_HOST=redis-cluster.internal
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}

# Vector Database
WEAVIATE_HOST=weaviate-cluster.internal
WEAVIATE_PORT=8080
WEAVIATE_SCHEME=http

# Elasticsearch
ELASTICSEARCH_HOST=elasticsearch-cluster.internal
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=${ELASTICSEARCH_PASSWORD}

# AI/ML Configuration
LLM_MODEL_PATH=/models/llama-2-7b-chat
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MAX_TOKENS=4096
TEMPERATURE=0.1

# Security
JWT_SECRET=${JWT_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
SESSION_TIMEOUT=1800

# Application
NODE_ENV=production
LOG_LEVEL=info
API_PORT=3000
CORS_ORIGIN=https://ai-copilot.fis.internal
```

### 4.2 Configuration Management

#### Using HashiCorp Vault
```bash
# Store secrets in Vault
vault kv put secret/ai-copilot/db \
  password="secure_db_password" \
  encryption_key="32_char_encryption_key"

vault kv put secret/ai-copilot/jwt \
  secret="jwt_signing_secret"

# Application retrieval
export DATABASE_PASSWORD=$(vault kv get -field=password secret/ai-copilot/db)
export JWT_SECRET=$(vault kv get -field=secret secret/ai-copilot/jwt)
```

---

## 5. Monitoring Setup

### 5.1 Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ai-copilot-api'
    static_configs:
      - targets: ['api-server:3000']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['elasticsearch:9200']
    metrics_path: /_prometheus/metrics

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 5.2 Grafana Dashboards

#### Key Metrics Dashboard
```json
{
  "dashboard": {
    "title": "AI Copilot System Overview",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Search Query Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(search_queries_total[5m]))",
            "legendFormat": "Queries/sec"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "singlestat",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends{datname=\"ai_copilot\"}"
          }
        ]
      }
    ]
  }
}
```

---

## 6. Backup & Recovery

### 6.1 Automated Backup Scripts

#### Database Backup
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -h $DATABASE_HOST -U $DATABASE_USER -d ai_copilot \
  --format=custom --compress=9 \
  --file="$BACKUP_DIR/postgres_$(date +%H%M%S).dump"

# Weaviate backup
curl -X POST "http://weaviate:8080/v1/backups/filesystem" \
  -H "Content-Type: application/json" \
  -d '{"id": "backup_'$(date +%Y%m%d_%H%M%S)'", "include": ["DocumentEmbedding", "QueryEmbedding"]}'

# Elasticsearch backup
curl -X PUT "elasticsearch:9200/_snapshot/backup_repo/snapshot_$(date +%Y%m%d_%H%M%S)" \
  -H "Content-Type: application/json" \
  -d '{"indices": "documents", "ignore_unavailable": true}'

# Upload to S3 or backup storage
aws s3 sync $BACKUP_DIR s3://fis-ai-copilot-backups/$(date +%Y%m%d)/
```

### 6.2 Recovery Procedures

#### Database Recovery
```bash
# PostgreSQL recovery
pg_restore -h $DATABASE_HOST -U $DATABASE_USER -d ai_copilot_restore \
  --clean --create /backups/postgres_backup.dump

# Weaviate recovery
curl -X POST "http://weaviate:8080/v1/backups/filesystem/backup_id/restore"

# Elasticsearch recovery
curl -X POST "elasticsearch:9200/_snapshot/backup_repo/snapshot_id/_restore"
```

---

## 7. Deployment Checklist

### 7.1 Pre-Deployment

- [ ] **Infrastructure Provisioning**
  - [ ] Servers provisioned and configured
  - [ ] Network connectivity verified
  - [ ] Security groups and firewall rules applied
  - [ ] SSL certificates installed

- [ ] **Database Setup**
  - [ ] PostgreSQL cluster deployed
  - [ ] Database schemas created
  - [ ] Initial data seeded
  - [ ] Backup procedures tested

- [ ] **Application Deployment**
  - [ ] Container images built and tested
  - [ ] Environment variables configured
  - [ ] Secrets management setup
  - [ ] Health checks configured

### 7.2 Post-Deployment

- [ ] **Verification Tests**
  - [ ] API endpoints responding
  - [ ] Database connectivity verified
  - [ ] Search functionality working
  - [ ] User authentication working

- [ ] **Monitoring Setup**
  - [ ] Prometheus collecting metrics
  - [ ] Grafana dashboards configured
  - [ ] Alerts configured and tested
  - [ ] Log aggregation working

- [ ] **Security Validation**
  - [ ] SSL certificates valid
  - [ ] Security scan completed
  - [ ] Access controls verified
  - [ ] Audit logging enabled

### 7.3 Performance Testing

```bash
# Load testing with K6
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },
    { duration: '5m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
};

export default function() {
  let response = http.post('https://ai-copilot.fis.internal/api/v1/search', 
    JSON.stringify({
      query: 'vacation policy',
      filters: { department: ['HR'] }
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 5s': (r) => r.timings.duration < 5000,
  });
}
```

---

## 8. Troubleshooting

### 8.1 Common Issues

#### High Memory Usage
```bash
# Check memory usage
docker stats
free -h

# Optimize JVM settings for Elasticsearch
echo "ES_JAVA_OPTS=-Xms4g -Xmx4g" >> /etc/elasticsearch/jvm.options

# Optimize PostgreSQL memory
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
```

#### Slow Search Performance
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Analyze query plans
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM documents 
WHERE content ILIKE '%vacation policy%';
```

### 8.2 Emergency Procedures

#### System Recovery
```bash
# Restart all services
docker-compose down
docker-compose up -d

# Check service health
curl -f http://localhost:3000/health
curl -f http://localhost:8080/v1/.well-known/ready
curl -f http://localhost:9200/_cluster/health
```

---

**Document Status**: Draft v1.0  
**Dependencies**: System Architecture, Database Design  
**Review Required**: Infrastructure Team, Security Team 