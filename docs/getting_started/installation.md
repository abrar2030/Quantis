# Installation Guide

This document provides detailed instructions for installing and setting up the Quantis time series forecasting platform in various environments.

## Prerequisites

Before installing Quantis, ensure your system meets the following requirements:

### System Requirements

- **CPU**: 4+ cores recommended for optimal performance
- **RAM**: Minimum 8GB, 16GB+ recommended for production use
- **Storage**: At least 20GB of free disk space
- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS 10.15+, or Windows 10/11 with WSL2

### Software Requirements

- **Python**: Version 3.8 or higher
- **Node.js**: Version 14 or higher
- **Docker**: Version 20.10 or higher (for containerized deployment)
- **Docker Compose**: Version 2.0 or higher (for containerized deployment)
- **Kubernetes**: Version 1.20+ (for production deployment)
- **Git**: For source code management

## Installation Methods

Quantis can be installed and run in several ways depending on your needs:

1. **Local Development Setup**: Install and run components directly on your machine
2. **Docker Compose**: Run the entire stack using containers
3. **Kubernetes**: Deploy to a Kubernetes cluster for production use

## Local Development Setup

Follow these steps to set up Quantis for local development:

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/quantis.git
cd quantis
```

### 2. Set Up Python Environment

It's recommended to use a virtual environment for Python dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install backend dependencies
pip install -r api/requirements.txt
```

### 3. Set Up Frontend Environment

```bash
# Navigate to the frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to the project root
cd ..
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=True
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
DATABASE_URL=sqlite:///./quantis.db

# Model Configuration
MODEL_PATH=./models/tft_model.pkl
```

Replace the placeholder values with your actual configuration.

### 5. Initialize the Database

```bash
# Run database initialization script
python -m api.db.init_db
```

### 6. Start the Backend Server

```bash
# Navigate to the API directory
cd api

# Start the FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Keep this terminal running and open a new one for the next steps
```

### 7. Start the Frontend Development Server

In a new terminal:

```bash
# Navigate to the frontend directory
cd frontend

# Start the React development server
npm start
```

The frontend will be available at http://localhost:3000, and the API will be at http://localhost:8000.

## Docker Compose Setup

For a containerized setup using Docker Compose:

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/quantis.git
cd quantis
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the necessary variables (similar to the local setup).

### 3. Build and Start the Containers

```bash
# Build and start all services
docker-compose up -d

# To view logs
docker-compose logs -f
```

This will start the following services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Database
- Redis (for caching)

### 4. Stop the Containers

```bash
docker-compose down
```

## Kubernetes Deployment

For production deployment on Kubernetes:

### 1. Clone the Repository

```bash
git clone https://github.com/your-organization/quantis.git
cd quantis
```

### 2. Configure Environment-Specific Values

Edit the values files in `infrastructure/kubernetes/environments/` for your target environment (dev, staging, or prod).

### 3. Apply Kubernetes Manifests

```bash
# For development environment
kubectl apply -k infrastructure/kubernetes/environments/dev

# For production environment
kubectl apply -k infrastructure/kubernetes/environments/prod
```

### 4. Verify Deployment

```bash
kubectl get pods
kubectl get services
```

## Terraform Deployment (Cloud Infrastructure)

To provision cloud infrastructure using Terraform:

### 1. Configure Terraform Variables

Edit the `terraform.tfvars` file in the appropriate environment directory:
- `infrastructure/terraform/environments/dev/terraform.tfvars`
- `infrastructure/terraform/environments/staging/terraform.tfvars`
- `infrastructure/terraform/environments/prod/terraform.tfvars`

### 2. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

### 3. Apply Terraform Configuration

```bash
# For development environment
cd environments/dev
terraform apply

# For production environment
cd environments/prod
terraform apply
```

## Troubleshooting

### Common Installation Issues

#### Python Dependency Errors

If you encounter errors installing Python dependencies:

```bash
# Update pip
pip install --upgrade pip

# Install wheel package
pip install wheel

# Try installing requirements again
pip install -r api/requirements.txt
```

#### Node.js Dependency Errors

If you encounter errors with Node.js dependencies:

```bash
# Clear npm cache
npm cache clean --force

# Try installing dependencies again
npm install
```

#### Docker Permission Issues

If you encounter permission issues with Docker:

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in for changes to take effect
```

#### Database Connection Issues

If the application cannot connect to the database:

1. Check that the database service is running
2. Verify the `DATABASE_URL` environment variable is correct
3. Ensure network connectivity between the application and database

### Getting Help

If you encounter issues not covered in this guide:

1. Check the project's GitHub issues for similar problems
2. Consult the troubleshooting section in the user manual
3. Contact the Quantis support team at support@quantis.example.com

## Next Steps

After installation, refer to the following documentation:

- [User Manual](../user_guides/user_manual.md) for using the Quantis platform
- [API Reference](../api/reference.md) for integrating with the API
- [Developer Guide](../getting_started/developer_guide.md) for contributing to the project

## Updating Quantis

To update an existing Quantis installation:

### Local Development

```bash
# Pull the latest changes
git pull

# Update backend dependencies
pip install -r api/requirements.txt

# Update frontend dependencies
cd frontend
npm install
```

### Docker Compose

```bash
# Pull the latest changes
git pull

# Rebuild and restart containers
docker-compose up -d --build
```

### Kubernetes

```bash
# Pull the latest changes
git pull

# Apply updated manifests
kubectl apply -k infrastructure/kubernetes/environments/your_environment
```
