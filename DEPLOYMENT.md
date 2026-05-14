# Deployment Guide

## Overview
This guide covers deploying the Workflow Intelligence Platform to production environments.

## Local Development

### Prerequisites
- Python 3.9+
- pip or conda
- Git

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/workflow-intelligence.git
cd workflow-intelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup
bash setup.sh  # On Windows: python setup.py
```

### Running Locally
```bash
# Terminal 1: Backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
streamlit run frontend/app.py --server.port 8501
```

### Access
- Dashboard: http://localhost:8501
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

---

## Docker Deployment

### Build Image
```bash
docker build -t workflow-intelligence:latest .
```

### Run Container
```bash
docker run -p 8000:8000 -p 8501:8501 \
  -v $(pwd)/output:/app/output \
  workflow-intelligence:latest
```

### Docker Compose
```bash
docker-compose up -d
```

### Access
- Dashboard: http://localhost:8501
- API: http://localhost:8000

---

## Cloud Deployment

### Render.com (Backend API)

#### Setup
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect your repository

#### Configuration
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**: See section below

#### Auto-Deploy
Enable auto-deploy on main branch.

### Streamlit Cloud (Frontend)

#### Setup
1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Create new app
4. Connect repository

#### Configuration
- **Repository**: Your GitHub repo
- **Branch**: main
- **Main file path**: frontend/app.py

#### Environment Variables
Create `.streamlit/secrets.toml`:
```toml
[server]
API_BASE_URL = "https://your-backend-api.onrender.com"
```

---

## Environment Variables

### Backend
```bash
# .env or export commands
PYTHON_ENV=production
DATABASE_URL=output/workflow_data.sqlite
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["https://your-domain.com"]
LOG_LEVEL=info
```

### Frontend (Streamlit secrets)
```toml
[server]
API_BASE_URL = "https://your-backend-api.onrender.com"

[client]
SHOW_SIDEBAR = true
```

---

## Production Recommendations

### Security
1. **Enable Authentication**
   ```python
   from fastapi.security import HTTPBearer
   security = HTTPBearer()
   ```

2. **HTTPS/TLS**
   - Use Let's Encrypt for SSL certificates
   - Redirect HTTP to HTTPS

3. **Database**
   - Use PostgreSQL instead of SQLite
   - Enable SSL connections
   - Regular backups

4. **API Keys**
   - Implement JWT tokens
   - Rate limiting
   - Request signing

### Performance
1. **Caching**
   ```python
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.redis import RedisBackend
   ```

2. **Database Optimization**
   - Add indexes
   - Query optimization
   - Connection pooling

3. **Content Delivery**
   - Use CDN for frontend assets
   - Enable gzip compression
   - Minify JavaScript/CSS

### Monitoring
1. **Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. **Error Tracking**
   - Sentry for error monitoring
   - CloudWatch for AWS
   - Datadog for observability

3. **Metrics**
   - Prometheus for metrics
   - Grafana for dashboards
   - New Relic for APM

### Database Migration
```bash
# For PostgreSQL upgrade
psql -U postgres -d workflow_db < schema.sql
```

---

## Scaling

### Horizontal Scaling
1. **Load Balancer**
   - Nginx or HAProxy
   - Route requests to multiple API instances

2. **Database Replication**
   - Read replicas for analytics
   - Write primary for generation

3. **Caching Layer**
   - Redis for session/data caching
   - Memcached alternative

### Vertical Scaling
- Increase compute resources
- Upgrade database size
- Optimize code

---

## Backup & Recovery

### Database Backups
```bash
# SQLite backup
cp output/workflow_data.sqlite output/workflow_data.backup.sqlite

# PostgreSQL backup
pg_dump workflow_db > backup.sql
```

### Restore
```bash
# SQLite restore
cp output/workflow_data.backup.sqlite output/workflow_data.sqlite

# PostgreSQL restore
psql workflow_db < backup.sql
```

### Schedule Automated Backups
```bash
# Cron job (Linux/Mac)
0 2 * * * cp /path/to/workflow_data.sqlite /backups/$(date +\%Y\%m\%d).sqlite
```

---

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker logs workflow-api

# Verify port availability
lsof -i :8000

# Test API health
curl http://localhost:8000/health
```

### Frontend Connection Issues
```bash
# Verify backend URL
streamlit run --logger.level=debug frontend/app.py

# Check network connectivity
curl http://backend-api:8000/health
```

### Database Locked
```bash
# SQLite database locked
rm output/workflow_data.sqlite-wal
rm output/workflow_data.sqlite-shm
```

---

## CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker image
        run: |
          docker build -t workflow-intelligence .
          docker push your-registry/workflow-intelligence:latest
      
      - name: Deploy to production
        run: |
          # Your deployment script
          bash scripts/deploy.sh
```

---

## Cost Optimization

### Render.com
- Use free tier for testing
- Pay-as-you-go for production
- Estimate: $10-50/month for small deployment

### Streamlit Cloud
- Free tier available
- Estimated: $0-20/month for hobby projects

### Database
- SQLite: Free (local storage)
- PostgreSQL: $15-100/month depending on tier

### Total Estimated Cost
- Small deployment: $20-70/month
- Medium deployment: $100-300/month
- Large deployment: $500+/month

---

## Maintenance

### Regular Tasks
- [ ] Monitor application logs
- [ ] Check API performance metrics
- [ ] Verify backup integrity
- [ ] Update dependencies monthly
- [ ] Review security logs
- [ ] Monitor disk space usage

### Monthly
- [ ] Security updates
- [ ] Dependency updates
- [ ] Performance optimization
- [ ] Database maintenance

### Quarterly
- [ ] Security audit
- [ ] Full backup test
- [ ] Disaster recovery drill
- [ ] Capacity planning

---

## Support & Troubleshooting

For issues:
1. Check deployment logs
2. Review API documentation
3. Test with manual requests
4. Check GitHub Issues
5. Contact support

---

**Last Updated:** May 2024
