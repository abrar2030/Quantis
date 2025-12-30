# Troubleshooting Guide

Common issues, error messages, and solutions for the Quantis platform.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Errors](#runtime-errors)
- [Database Issues](#database-issues)
- [API Errors](#api-errors)
- [Model Training Issues](#model-training-issues)
- [Performance Problems](#performance-problems)
- [Docker/Kubernetes Issues](#dockerkubernetes-issues)
- [Network & Connectivity](#network--connectivity)
- [Debug Mode & Logging](#debug-mode--logging)

---

## Installation Issues

### Issue: `ModuleNotFoundError: No module named 'api'`

**Symptom**: Import errors when running the application

**Cause**: Python path not configured correctly

**Solution**:

```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/Quantis/code:$PYTHONPATH

# Or run from code directory
cd /path/to/Quantis/code
python -m api.app

# For tests
cd /path/to/Quantis
PYTHONPATH=$(pwd)/code pytest tests/
```

### Issue: `ModuleNotFoundError: No module named 'pyotp'`

**Symptom**: Missing Python dependencies

**Cause**: Requirements not installed or wrong virtual environment

**Solution**:

```bash
# Activate virtual environment
source code/api/venv/bin/activate

# Install/reinstall requirements
pip install -r code/api/requirements.txt

# If issues persist, recreate venv
rm -rf code/api/venv
python3 -m venv code/api/venv
source code/api/venv/bin/activate
pip install --upgrade pip
pip install -r code/api/requirements.txt
```

### Issue: npm install fails with `EACCES` error

**Symptom**: Permission errors during npm install

**Cause**: npm global directory permissions issue

**Solution**:

```bash
# Fix npm permissions
sudo chown -R $USER:$GROUP ~/.npm
sudo chown -R $USER:$GROUP ~/.config

# Or use nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 16
nvm use 16
```

### Issue: Scripts not executable

**Symptom**: `Permission denied` when running .sh scripts

**Cause**: Execute permission not set

**Solution**:

```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Or use the provided script
./scripts/make_scripts_executable.sh

# If that fails
bash scripts/make_scripts_executable.sh
```

---

## Runtime Errors

### Issue: `Address already in use` (Port 8000/3000)

**Symptom**: Cannot start API/frontend - port already bound

**Cause**: Another process is using the port

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000
# Or: netstat -tulpn | grep :8000

# Kill the process
kill -9 <PID>

# Or use different port
# For API:
uvicorn api.app:app --port 8001

# For frontend:
PORT=3001 npm start
```

### Issue: `RuntimeError: Event loop is closed`

**Symptom**: Async errors in FastAPI

**Cause**: Improper async/await usage or event loop issues

**Solution**:

```bash
# Ensure you're using supported Python version
python --version  # Should be 3.9+

# Check uvicorn installation
pip install --upgrade uvicorn[standard]

# Run with explicit event loop policy
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

### Issue: `OperationalError: unable to open database file`

**Symptom**: SQLite database access errors

**Cause**: Permission issues or missing directory

**Solution**:

```bash
# Check database directory exists
mkdir -p code/api

# Check permissions
chmod 755 code/api
touch code/api/quantis.db
chmod 644 code/api/quantis.db

# Verify DATABASE_URL
echo $DATABASE_URL
# Should be: sqlite:///./quantis.db
```

---

## Database Issues

### Issue: `FATAL: password authentication failed for user`

**Symptom**: Cannot connect to PostgreSQL

**Cause**: Incorrect credentials or connection string

**Solution**:

```bash
# Verify DATABASE_URL format
export DATABASE_URL="postgresql://username:password@host:5432/dbname"

# Test connection
psql $DATABASE_URL

# Or test with Python
python -c "from api.database import health_check; print(health_check())"

# Check PostgreSQL is running
sudo systemctl status postgresql
```

### Issue: `Too many open connections`

**Symptom**: Database connection pool exhausted

**Cause**: Connection leaks or insufficient pool size

**Solution**:

```python
# In .env file, adjust pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=60

# Check for connection leaks in code
# Always use context managers:
with get_db() as db:
    # Do work
    pass
```

### Issue: Migration errors

**Symptom**: Database schema out of sync

**Cause**: Missing migrations or incorrect migration order

**Solution**:

```bash
# Check current revision
alembic current

# Run migrations
alembic upgrade head

# If issues, recreate database (DEV ONLY!)
rm code/api/quantis.db
python -c "from api.database import init_db; init_db()"
```

---

## API Errors

### Issue: `401 Unauthorized` on all requests

**Symptom**: All authenticated requests fail

**Cause**: Invalid or expired JWT token

**Solution**:

```bash
# Re-authenticate
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_user", "password": "your_pass"}'

# Check token expiration
# Decode JWT at: https://jwt.io
# Verify exp claim hasn't passed

# Ensure clock sync (server/client)
timedatectl status
```

### Issue: `422 Unprocessable Entity` errors

**Symptom**: Request validation failures

**Cause**: Invalid input data or missing required fields

**Solution**:

```bash
# Check API documentation
curl http://localhost:8000/docs

# Examine error response details
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}

# Fix input data according to error message
```

### Issue: `429 Too Many Requests`

**Symptom**: Rate limit exceeded

**Cause**: Too many requests in short time window

**Solution**:

```python
# Implement exponential backoff
import time
import requests

def api_call_with_retry(url, max_retries=3):
    for i in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            wait_time = 2 ** i  # Exponential backoff
            time.sleep(wait_time)
            continue
        return response
    raise Exception("Max retries exceeded")
```

### Issue: `500 Internal Server Error`

**Symptom**: Generic server error

**Cause**: Unhandled exception in API code

**Solution**:

```bash
# Enable debug mode (DEV ONLY!)
export DEBUG=True

# Check API logs
docker-compose logs -f api
# Or
tail -f /var/log/quantis/api.log

# Look for stack traces
grep -A 20 "ERROR" /var/log/quantis/api.log
```

---

## Model Training Issues

### Issue: Training takes too long or hangs

**Symptom**: Model training never completes

**Cause**: Large dataset, insufficient resources, or configuration issue

**Solution**:

```python
# Reduce batch size
{
  "batch_size": 16,  # Instead of 32 or 64
  "epochs": 50       # Reduce epochs for testing
}

# Use smaller dataset for testing
dataset_sample = dataset.sample(n=1000)

# Check system resources
htop  # CPU usage
nvidia-smi  # GPU usage (if applicable)

# Monitor training progress
curl http://localhost:8000/models/1/training-status
```

### Issue: `CUDA out of memory` error

**Symptom**: GPU memory exhausted during training

**Cause**: Batch size too large for available GPU memory

**Solution**:

```python
# Reduce batch size
params["batch_size"] = 8  # Start small

# Use gradient accumulation
# Effective batch size = batch_size * accumulation_steps

# Clear GPU cache between runs
import torch
torch.cuda.empty_cache()

# Monitor GPU memory
watch -n 1 nvidia-smi
```

### Issue: Model accuracy is very low

**Symptom**: Poor model performance despite training

**Cause**: Data issues, hyperparameters, or model architecture mismatch

**Solution**:

```bash
# Check data quality
curl http://localhost:8000/datasets/1/stats

# Verify data preprocessing
# - Check for NaN values
# - Verify scaling/normalization
# - Check train/test split

# Try different hyperparameters
{
  "learning_rate": 0.0001,  # Lower learning rate
  "hidden_size": 128,        # Increase capacity
  "dropout": 0.2             # Regularization
}

# Use MLflow to track experiments
# Access: http://localhost:5000
```

---

## Performance Problems

### Issue: Slow API response times

**Symptom**: Requests taking > 5 seconds

**Cause**: Inefficient queries, missing indexes, or overloaded server

**Solution**:

```sql
-- Add database indexes
CREATE INDEX idx_predictions_model_id ON predictions(model_id);
CREATE INDEX idx_predictions_created_at ON predictions(created_at);

-- Check slow queries
-- In PostgreSQL:
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

```python
# Enable query logging
# In code/api/database.py
engine = create_engine(
    DATABASE_URL,
    echo=True  # Log all SQL queries
)

# Use eager loading for relationships
from sqlalchemy.orm import joinedload

models = db.query(Model).options(
    joinedload(Model.predictions)
).all()
```

### Issue: High memory usage

**Symptom**: Server running out of memory

**Cause**: Memory leaks, large datasets in memory, or caching issues

**Solution**:

```bash
# Monitor memory
free -h
htop

# Check for leaks
python -m memory_profiler api/app.py

# Adjust worker count
uvicorn api.app:app --workers 2  # Reduce workers

# Configure Redis maxmemory
redis-cli CONFIG SET maxmemory 1gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Issue: Database connection timeouts

**Symptom**: `TimeoutError` when accessing database

**Cause**: Pool exhaustion or slow queries

**Solution**:

```bash
# Increase pool size
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=60

# Add connection health checks
DB_POOL_PRE_PING=True

# Optimize queries
# Use EXPLAIN to analyze query plans
```

---

## Docker/Kubernetes Issues

### Issue: Container fails to start

**Symptom**: Container exits immediately

**Cause**: Configuration error or missing dependencies

**Solution**:

```bash
# Check container logs
docker logs <container-name>

# Inspect container
docker inspect <container-name>

# Try running interactively
docker run -it <image-name> /bin/bash

# Check docker-compose syntax
docker-compose config

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Kubernetes pods in `CrashLoopBackOff`

**Symptom**: Pods continuously restarting

**Cause**: Application crashes, health check failures, or resource limits

**Solution**:

```bash
# Check pod logs
kubectl logs <pod-name> -n quantis

# Describe pod for events
kubectl describe pod <pod-name> -n quantis

# Check resource limits
kubectl top pods -n quantis

# Adjust resource limits in deployment
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Issue: Volume mount permissions

**Symptom**: Permission denied accessing mounted volumes

**Cause**: User ID mismatch between container and host

**Solution**:

```bash
# In Dockerfile, set user
USER 1000:1000

# Or fix permissions on host
sudo chown -R 1000:1000 /path/to/volume

# For Kubernetes, use securityContext
securityContext:
  fsGroup: 1000
  runAsUser: 1000
```

---

## Network & Connectivity

### Issue: Cannot access API from browser

**Symptom**: Connection refused or timeout

**Cause**: Firewall, wrong host, or service not running

**Solution**:

```bash
# Verify service is running
curl http://localhost:8000/health
# Or
netstat -tulpn | grep 8000

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp

# Verify binding address
# API should bind to 0.0.0.0, not 127.0.0.1

# For Docker, check port mapping
docker-compose ps
docker port <container-name>
```

### Issue: CORS errors in browser

**Symptom**: Browser blocks API requests

**Cause**: Cross-origin restrictions

**Solution**:

```bash
# Update CORS settings in .env
CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# For development, allow all origins
CORS_ORIGINS=["*"]

# Verify in browser console
# Check Access-Control-Allow-Origin header
```

### Issue: WebSocket connection fails

**Symptom**: WebSocket handshake error

**Cause**: Protocol mismatch, proxy issues, or authentication failure

**Solution**:

```javascript
// Ensure correct protocol
const ws = new WebSocket('ws://localhost:8000/ws/notifications');

// Include auth token
const token = 'your-jwt-token';
const ws = new WebSocket(`ws://localhost:8000/ws/notifications?token=${token}`);

// Handle errors
ws.onerror = (error) => console.error('WebSocket error:', error);
```

---

## Debug Mode & Logging

### Enable Debug Logging

```bash
# In .env file
DEBUG=True
LOG_LEVEL=DEBUG
LOG_FORMAT=text  # More readable than JSON

# Restart services
./scripts/run_quantis.sh dev
```

### View Logs

```bash
# API logs (if running with scripts)
tail -f /var/log/quantis/api.log

# Docker logs
docker-compose logs -f api

# Kubernetes logs
kubectl logs -f deployment/api -n quantis

# Follow logs in real-time
kubectl logs -f -l app=quantis-api -n quantis --tail=100
```

### Structured Logging

```python
# In application code
import structlog
logger = structlog.get_logger(__name__)

logger.info("user_login", user_id=user.id, ip=request.client.host)
logger.error("prediction_failed", model_id=model_id, error=str(e))
```

---

## Getting Help

If you can't resolve an issue:

1. **Check logs** first - most issues have clear error messages
2. **Search GitHub Issues**: [github.com/abrar2030/Quantis/issues](https://github.com/abrar2030/Quantis/issues)
3. **Review Documentation**: Ensure you followed setup instructions correctly
4. **Minimal Reproducible Example**: Create a simple test case
5. **Open an Issue**: Provide:
   - Operating system and version
   - Python/Node.js version
   - Exact error message and stack trace
   - Steps to reproduce
   - Configuration (sanitized, no secrets!)

---

## Common Error Messages Reference

| Error Message               | Likely Cause                           | Section                                  |
| --------------------------- | -------------------------------------- | ---------------------------------------- |
| `ModuleNotFoundError`       | Missing dependency or wrong PYTHONPATH | [Installation](#installation-issues)     |
| `Address already in use`    | Port conflict                          | [Runtime](#runtime-errors)               |
| `401 Unauthorized`          | Invalid/expired token                  | [API Errors](#api-errors)                |
| `422 Unprocessable Entity`  | Validation failure                     | [API Errors](#api-errors)                |
| `500 Internal Server Error` | Unhandled exception                    | [API Errors](#api-errors)                |
| `CUDA out of memory`        | GPU memory exhausted                   | [Model Training](#model-training-issues) |
| `CrashLoopBackOff`          | Pod crashes repeatedly                 | [Kubernetes](#dockerkubernetes-issues)   |
| `Connection refused`        | Service not running/firewall           | [Network](#network--connectivity)        |

---
