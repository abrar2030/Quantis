# Installation Guide

Complete installation instructions for the Quantis platform across different environments and operating systems.

## Table of Contents

- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Installation Options](#installation-options)
- [Method 1: Automated Setup (Recommended)](#method-1-automated-setup-recommended)
- [Method 2: Manual Local Setup](#method-2-manual-local-setup)
- [Method 3: Docker Compose](#method-3-docker-compose)
- [Method 4: Kubernetes Production Deployment](#method-4-kubernetes-production-deployment)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure the following software is installed before proceeding:

| Software       | Minimum Version | Recommended | Purpose                          |
| -------------- | --------------- | ----------- | -------------------------------- |
| Python         | 3.9             | 3.11+       | Backend API and ML models        |
| Node.js        | 14.x            | 16.x+       | Frontend web application         |
| npm            | 6.x             | 8.x+        | Frontend package management      |
| Docker         | 20.10           | Latest      | Containerized deployment         |
| Docker Compose | 2.0             | Latest      | Multi-container orchestration    |
| Git            | 2.x             | Latest      | Version control                  |
| Kubernetes     | 1.20+           | 1.25+       | Production deployment (optional) |

---

## System Requirements

### Development Environment

| Component   | Minimum                                                | Recommended      |
| ----------- | ------------------------------------------------------ | ---------------- |
| **CPU**     | 2 cores                                                | 4+ cores         |
| **RAM**     | 8 GB                                                   | 16 GB            |
| **Storage** | 10 GB free                                             | 20 GB+ free      |
| **OS**      | Ubuntu 20.04+ / macOS 10.15+ / Windows 10/11 with WSL2 | Ubuntu 22.04 LTS |

### Production Environment

| Component   | Minimum   | Recommended      |
| ----------- | --------- | ---------------- |
| **CPU**     | 4 cores   | 8+ cores         |
| **RAM**     | 16 GB     | 32 GB+           |
| **Storage** | 50 GB SSD | 100 GB+ NVMe SSD |
| **Network** | 100 Mbps  | 1 Gbps+          |

---

## Installation Options

Choose the installation method that best fits your use case:

| Method                                                   | Use Case                  | Complexity | Setup Time |
| -------------------------------------------------------- | ------------------------- | ---------- | ---------- |
| [Automated Setup](#method-1-automated-setup-recommended) | Quick development start   | Low        | 5-10 min   |
| [Manual Local](#method-2-manual-local-setup)             | Custom development setup  | Medium     | 15-20 min  |
| [Docker Compose](#method-3-docker-compose)               | Containerized development | Low        | 10-15 min  |
| [Kubernetes](#method-4-kubernetes-production-deployment) | Production deployment     | High       | 30-60 min  |

---

## Method 1: Automated Setup (Recommended)

The fastest way to get started with Quantis for development.

### Step 1: Clone Repository

```bash
git clone https://github.com/quantsingularity/Quantis.git
cd Quantis
```

### Step 2: Run Setup Script

```bash
chmod +x scripts/setup_quantis_env.sh
./scripts/setup_quantis_env.sh
```

The script automatically:

- Creates Python virtual environments
- Installs all Python dependencies
- Installs Node.js dependencies
- Sets up configuration files

### Step 3: Start Services

```bash
chmod +x scripts/run_quantis.sh
./scripts/run_quantis.sh dev
```

**Access Points:**

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

---

## Method 2: Manual Local Setup

For developers who want fine-grained control over the installation.

### Step 1: Clone Repository

```bash
git clone https://github.com/quantsingularity/Quantis.git
cd Quantis
```

### Step 2: Backend Setup

```bash
# Navigate to API directory
cd code/api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Return to project root
cd ../..
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd web-frontend

# Install dependencies
npm install

# Return to project root
cd ..
```

### Step 4: Configuration

Create `.env` file in `code/api/` directory:

```bash
# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET=your-jwt-secret-change-in-production

# Database
DATABASE_URL=sqlite:///./quantis.db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-password

# API Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Step 5: Initialize Database

```bash
cd code
PYTHONPATH=/path/to/Quantis/code:$PYTHONPATH python -m api.database
cd ..
```

### Step 6: Start Services

**Terminal 1 - Backend:**

```bash
cd code
source api/venv/bin/activate
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**

```bash
cd web-frontend
npm start
```

---

## Method 3: Docker Compose

For containerized development with minimal host dependencies.

### Step 1: Prerequisites

Ensure Docker and Docker Compose are installed:

```bash
docker --version
docker-compose --version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/quantsingularity/Quantis.git
cd Quantis
```

### Step 3: Configure Environment

Edit `infrastructure/docker-compose.yml` if needed. Default configuration includes:

- API service (port 8000)
- Frontend service (port 80)
- MLflow (port 5000)
- Prometheus (port 9090)
- Grafana (port 3000)

### Step 4: Build and Start

```bash
cd infrastructure
docker-compose up -d --build
```

### Step 5: Verify Services

```bash
docker-compose ps
docker-compose logs -f api
```

**Access Points:**

- Frontend: http://localhost:80
- API: http://localhost:8000
- MLflow: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

### Stop Services

```bash
docker-compose down
# With volume cleanup:
docker-compose down -v
```

---

## Method 4: Kubernetes Production Deployment

For scalable production deployments using Kubernetes.

### Step 1: Prerequisites

```bash
# Verify Kubernetes cluster access
kubectl cluster-info
kubectl get nodes

# Verify Helm (if using)
helm version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/quantsingularity/Quantis.git
cd Quantis/infrastructure/kubernetes
```

### Step 3: Configure Environment

Edit configuration for your environment:

```bash
# Development
cd environments/dev
vim config.yaml

# Production
cd environments/prod
vim config.yaml
```

### Step 4: Deploy to Kubernetes

```bash
# Deploy development environment
kubectl apply -k infrastructure/kubernetes/

# Or use specific environment
kubectl apply -k infrastructure/kubernetes/environments/dev

# For production
kubectl apply -k infrastructure/kubernetes/environments/prod
```

### Step 5: Verify Deployment

```bash
# Check pods
kubectl get pods -n quantis

# Check services
kubectl get services -n quantis

# Check ingress
kubectl get ingress -n quantis
```

### Step 6: Access Services

```bash
# Port forward for testing
kubectl port-forward -n quantis svc/api-service 8000:8000
kubectl port-forward -n quantis svc/frontend-service 3000:80
```

---

## Verification

After installation, verify the setup:

### 1. Check Backend API

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

### 2. Check API Documentation

Navigate to: http://localhost:8000/docs

### 3. Check Frontend

Navigate to: http://localhost:3000

### 4. Run Test Suite (Optional)

```bash
cd Quantis
PYTHONPATH=/path/to/Quantis/code:$PYTHONPATH pytest tests/
```

---

## Troubleshooting

### Common Issues

#### Python Dependency Errors

**Issue**: `ModuleNotFoundError` or dependency conflicts

**Solution**:

```bash
# Upgrade pip
pip install --upgrade pip

# Clear cache
pip cache purge

# Reinstall requirements
pip install --no-cache-dir -r requirements.txt
```

#### Node.js Dependency Errors

**Issue**: npm install fails or version conflicts

**Solution**:

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### Port Already in Use

**Issue**: `Address already in use` error

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000
# Or on Windows: netstat -ano | findstr :8000

# Kill the process
kill -9 <PID>
```

#### Docker Permission Denied

**Issue**: Permission errors when running Docker commands

**Solution**:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

#### Database Connection Errors

**Issue**: Cannot connect to database

**Solution**:

1. Verify DATABASE_URL in `.env` file
2. Check database service is running:

   ```bash
   # For SQLite (default)
   ls -la code/api/quantis.db

   # For PostgreSQL
   pg_isready -h localhost -p 5432
   ```

#### Memory Issues During Installation

**Issue**: Installation crashes due to insufficient memory

**Solution**:

```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"

# Install with limited concurrency
npm install --maxsockets 1
```

---

## Installation Table by OS

| OS / Platform        | Recommended Install Command                   | Notes                                            |
| -------------------- | --------------------------------------------- | ------------------------------------------------ |
| **Ubuntu 20.04+**    | `./scripts/setup_quantis_env.sh`              | Fully supported, recommended for production      |
| **Ubuntu 22.04 LTS** | `./scripts/setup_quantis_env.sh`              | Best tested, primary dev platform                |
| **macOS 11+**        | `./scripts/setup_quantis_env.sh`              | Install Xcode Command Line Tools first           |
| **macOS M1/M2**      | Manual setup recommended                      | Some dependencies may need `arch -x86_64` prefix |
| **Windows 10/11**    | Use WSL2 + Ubuntu                             | Install WSL2, then follow Ubuntu instructions    |
| **Docker (Any OS)**  | `docker-compose up -d`                        | Isolated environment, no host dependencies       |
| **Kubernetes**       | `kubectl apply -k infrastructure/kubernetes/` | Requires cluster access and configuration        |

---

## Post-Installation

After successful installation:

1. **Configure environment variables** - See [Configuration Guide](CONFIGURATION.md)
2. **Read usage documentation** - See [Usage Guide](USAGE.md)
3. **Explore examples** - See [Examples](examples/)
4. **Set up monitoring** - Configure Prometheus and Grafana dashboards

---

## Next Steps

- [Configuration Guide](CONFIGURATION.md) - Configure Quantis for your environment
- [Usage Guide](USAGE.md) - Learn common workflows
- [API Reference](API.md) - Explore the REST API
- [Troubleshooting](TROUBLESHOOTING.md) - Get help with common issues

---
