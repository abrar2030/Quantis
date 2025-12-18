# Kubernetes Deployment Guide

## Prerequisites

- kubectl v1.24+
- Access to a Kubernetes cluster
- Docker images built and pushed to registry

## Setup Steps

### 1. Configure Secrets

```bash
# Copy the example secrets file
cp base/app-secrets.example.yaml base/app-secrets.yaml

# Edit the file and replace all CHANGE_ME values
vi base/app-secrets.yaml

# Apply secrets (DO NOT commit app-secrets.yaml)
kubectl apply -f base/app-secrets.yaml
```

### 2. Update Image Registry

Edit deployment files and replace `YOUR_REGISTRY_URL` with your actual container registry:

```bash
# backend-deployment.yaml
sed -i 's|YOUR_REGISTRY_URL|your.registry.com|g' base/backend-deployment.yaml

# frontend-deployment.yaml
sed -i 's|YOUR_REGISTRY_URL|your.registry.com|g' base/frontend-deployment.yaml
```

### 3. Validate Manifests

```bash
# Validate YAML syntax
yamllint base/*.yaml

# Dry-run to check for errors
kubectl apply --dry-run=client -f base/
```

### 4. Deploy Application

```bash
# Apply all base manifests
kubectl apply -f base/

# Check deployment status
kubectl get pods
kubectl get services
kubectl get ingress
```

### 5. Verify Deployment

```bash
# Check pod logs
kubectl logs -l app=backend
kubectl logs -l app=frontend

# Check service endpoints
kubectl get endpoints
```

## Environment-Specific Deployments

### Development

```bash
kubectl apply -f environments/dev/values.yaml
```

### Staging

```bash
kubectl apply -f environments/staging/values.yaml
```

### Production

```bash
kubectl apply -f environments/prod/values.yaml
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Service not accessible

```bash
kubectl describe service <service-name>
kubectl get endpoints <service-name>
```

### Ingress issues

```bash
kubectl describe ingress quantis-ingress
kubectl logs -n ingress-nginx <ingress-controller-pod>
```

## Clean Up

```bash
# Delete all resources
kubectl delete -f base/

# Delete secrets
kubectl delete secret app-secrets
```
