# Infrastructure Documentation

This document provides comprehensive information about the infrastructure components of the Quantis time series forecasting platform, including deployment options, configuration, and management.

## Overview

The Quantis platform is designed with a modern, cloud-native architecture that can be deployed in various environments, from local development to large-scale production deployments. The infrastructure is defined as code, enabling consistent, repeatable deployments and infrastructure management.

## Deployment Options

Quantis supports multiple deployment options to accommodate different use cases and organizational requirements:

### Local Development

For development and testing purposes, Quantis can be run locally using:

- Individual component execution (API, frontend, etc.)
- Docker Compose for containerized local deployment

### Container Orchestration

For production deployments, Quantis uses Kubernetes for container orchestration:

- Scalable, resilient deployment
- Resource optimization
- Service discovery and load balancing
- Automated rollouts and rollbacks

### Cloud Providers

Quantis can be deployed on major cloud providers:

- **AWS**: Using EKS for Kubernetes, RDS for databases, S3 for storage
- **Azure**: Using AKS for Kubernetes, Azure SQL for databases, Blob Storage for storage
- **Google Cloud**: Using GKE for Kubernetes, Cloud SQL for databases, Cloud Storage for storage

### On-Premises

For organizations with specific security or compliance requirements, Quantis supports on-premises deployment:

- Kubernetes on bare metal or virtualized infrastructure
- Integration with existing monitoring and security systems
- Support for air-gapped environments

## Infrastructure Components

### Docker Containers

Quantis uses Docker containers for packaging and deployment:

#### API Container

The API container runs the FastAPI backend service:

- Base image: Python 3.8
- Exposed port: 8000
- Environment variables for configuration
- Health check endpoint: `/health`

#### Frontend Container

The frontend container serves the React web application:

- Base image: Node.js for building, Nginx for serving
- Exposed port: 80
- Static content served through Nginx
- Configuration through environment variables

#### Model Serving Container

Dedicated container for model inference:

- Base image: Python with ML libraries
- Exposed port: 8001
- GPU support (optional)
- Model artifacts mounted as volumes

### Kubernetes Resources

The Kubernetes deployment includes:

#### Deployments

- `frontend-deployment`: React frontend application
- `backend-deployment`: FastAPI backend service
- `model-deployment`: Model serving component

#### Services

- `frontend-service`: Exposes frontend to users
- `backend-service`: Internal service for API
- `model-service`: Internal service for model inference

#### ConfigMaps and Secrets

- `app-configmap`: Application configuration
- `app-secrets`: Sensitive information (credentials, keys)

#### StatefulSets

- `database-statefulset`: Database with persistent storage

#### Persistent Volumes

- Database storage
- Model artifacts storage
- Logging storage

#### Ingress

- External access configuration
- TLS termination
- Path-based routing

### Terraform Infrastructure

Quantis uses Terraform to provision and manage cloud infrastructure:

#### Network Module

- VPC/VNET configuration
- Subnets for different components
- Security groups/Network security groups
- Load balancers

#### Compute Module

- Kubernetes cluster configuration
- Node pools with autoscaling
- Instance types and sizing

#### Database Module

- Managed database services
- Backup configuration
- High availability setup

#### Storage Module

- Object storage for artifacts and backups
- Block storage for persistent data
- Access controls and policies

#### Security Module

- IAM roles and policies
- Key management
- Security monitoring

## Configuration Management

### Environment-Specific Configuration

Quantis uses a hierarchical configuration approach:

1. **Base Configuration**: Default settings applicable to all environments
2. **Environment Overrides**: Settings specific to dev, staging, or production
3. **Secret Management**: Sensitive information stored securely

### Configuration Files

Key configuration files include:

#### Docker Compose

`docker-compose.yml` defines the local development environment:

```yaml
version: '3'
services:
  api:
    build:
      context: ./api
      dockerfile: ../infrastructure/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/quantis
      - DEBUG=true
    volumes:
      - ./api:/app
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: ../infrastructure/Dockerfile.frontend
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/app
    depends_on:
      - api

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=quantis
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Kubernetes Manifests

Example of a Kubernetes deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  namespace: quantis
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: api
        image: quantis/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Terraform Configuration

Example of a Terraform configuration file:

```hcl
module "kubernetes_cluster" {
  source = "../modules/compute"

  cluster_name     = "quantis-${var.environment}"
  kubernetes_version = "1.21"
  region           = var.region
  node_pools = [
    {
      name       = "general"
      node_count = 3
      vm_size    = "Standard_D4s_v3"
    },
    {
      name       = "ml"
      node_count = 2
      vm_size    = "Standard_NC6s_v3"
    }
  ]

  tags = {
    Environment = var.environment
    Application = "Quantis"
  }
}
```

## Deployment Process

### CI/CD Pipeline

Quantis uses a CI/CD pipeline for automated testing and deployment:

1. **Code Commit**: Changes pushed to version control
2. **Automated Tests**: Unit and integration tests run
3. **Build**: Docker images built and tagged
4. **Push**: Images pushed to container registry
5. **Deploy**: Infrastructure updated via Terraform and Kubernetes manifests

### Deployment Workflow

The deployment process follows these steps:

1. **Infrastructure Provisioning**:
   ```bash
   cd infrastructure/terraform/environments/dev
   terraform init
   terraform apply
   ```

2. **Kubernetes Deployment**:
   ```bash
   kubectl apply -k infrastructure/kubernetes/environments/dev
   ```

3. **Verification**:
   ```bash
   kubectl get pods -n quantis
   kubectl get services -n quantis
   ```

### Rollback Procedure

In case of deployment issues:

1. **Kubernetes Rollback**:
   ```bash
   kubectl rollout undo deployment/backend-deployment -n quantis
   ```

2. **Infrastructure Rollback**:
   ```bash
   terraform apply -target=module.kubernetes_cluster -var-file=previous.tfvars
   ```

## Scaling and High Availability

### Horizontal Scaling

Quantis components can scale horizontally:

- API and frontend services scale based on CPU/memory usage
- Model serving scales based on prediction request volume
- Database connections pool adjusts to service instances

### Vertical Scaling

For components with specific resource needs:

- Model training can use larger instances with more CPU/GPU
- Database instances can be upgraded for more capacity
- Caching layer can be expanded for better performance

### High Availability

Quantis ensures high availability through:

- Multi-zone deployment across availability zones
- Database replication and failover
- Stateless service design for easy replacement
- Load balancing across multiple instances

## Monitoring and Logging

### Infrastructure Monitoring

Quantis uses Prometheus and Grafana for monitoring:

- Resource utilization (CPU, memory, disk)
- Network traffic and latency
- Container health and restarts
- Node status and availability

### Application Logging

Centralized logging with:

- Structured JSON logs
- Log aggregation (ELK stack or cloud provider solutions)
- Log retention policies
- Log-based alerting

### Alerting

Alert configuration for:

- Service availability issues
- Resource constraints
- Error rate thresholds
- Performance degradation

## Security

### Network Security

- Private subnets for internal components
- Security groups limiting access
- Network policies in Kubernetes
- TLS for all external and internal communication

### Authentication and Authorization

- RBAC for Kubernetes resources
- IAM policies for cloud resources
- Service accounts with minimal permissions
- Secret rotation policies

### Compliance

Support for various compliance requirements:

- Data residency controls
- Audit logging
- Encryption at rest and in transit
- Backup and disaster recovery

## Disaster Recovery

### Backup Strategy

- Database: Daily full backups, continuous transaction logs
- Object Storage: Versioning and cross-region replication
- Configuration: Infrastructure as code in version control

### Recovery Procedures

- Database: Point-in-time recovery
- Application: Redeployment from container images
- Infrastructure: Recreation from Terraform code

### Recovery Time Objectives

- Tier 1 (Critical): < 1 hour
- Tier 2 (Important): < 4 hours
- Tier 3 (Non-critical): < 24 hours

## Cost Optimization

### Resource Efficiency

- Right-sizing of instances
- Autoscaling based on demand
- Spot instances for batch processing
- Reserved instances for predictable workloads

### Cost Monitoring

- Tagging strategy for cost allocation
- Budget alerts and anomaly detection
- Regular cost review and optimization

## Troubleshooting

### Common Issues

#### Pod Startup Failures

Check for:
- Resource constraints
- Image pull errors
- Configuration issues

Resolution:
```bash
kubectl describe pod <pod-name> -n quantis
kubectl logs <pod-name> -n quantis
```

#### Database Connection Issues

Check for:
- Network connectivity
- Credential issues
- Connection pool exhaustion

Resolution:
```bash
kubectl exec -it <api-pod> -n quantis -- curl -v <db-service>:5432
kubectl get secret app-secrets -n quantis -o yaml
```

#### Performance Degradation

Check for:
- Resource utilization
- Slow database queries
- External service dependencies

Resolution:
```bash
kubectl top pods -n quantis
kubectl exec -it <db-pod> -n quantis -- psql -U postgres -c "SELECT * FROM pg_stat_activity"
```

## Future Infrastructure Enhancements

Planned improvements to the infrastructure:

1. **Service Mesh**: Implementation of Istio for advanced traffic management
2. **GitOps**: Adoption of ArgoCD for declarative deployments
3. **Serverless Components**: Integration of serverless functions for event-driven processes
4. **Multi-Cluster Federation**: Support for global distribution of services
5. **Advanced Autoscaling**: Predictive scaling based on historical patterns

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform Documentation](https://www.terraform.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [React Deployment Best Practices](https://create-react-app.dev/docs/deployment/)
