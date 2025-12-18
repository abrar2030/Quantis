# Quantis Infrastructure

Comprehensive infrastructure as code for the Quantis trading platform.

## Directory Structure

```
infrastructure/
├── README.md                    # This file
├── terraform/                   # Infrastructure as Code
│   ├── main.tf                 # Main configuration
│   ├── variables.tf            # Variable definitions
│   ├── outputs.tf              # Output definitions
│   ├── terraform.tfvars.example # Example configuration
│   ├── environments/           # Environment-specific configs
│   │   ├── dev/
│   │   ├── staging/
│   │   └── prod/
│   └── modules/                # Reusable modules
│       ├── compute/
│       ├── database/
│       ├── network/
│       ├── security/
│       └── storage/
├── kubernetes/                  # Container orchestration
│   ├── README.md
│   ├── base/                   # Base manifests
│   └── environments/           # Environment overlays
├── ansible/                     # Configuration management
│   ├── README.md
│   ├── inventory/
│   ├── playbooks/
│   └── roles/
├── ci-cd/                      # CI/CD pipelines
│   └── ci-cd.yml
├── docker-compose.yml          # Local development
```

## Prerequisites

### Required Tools

- **Terraform** v1.0+ - [Install](https://www.terraform.io/downloads)
- **kubectl** v1.24+ - [Install](https://kubernetes.io/docs/tasks/tools/)
- **Ansible** v2.10+ - [Install](https://docs.ansible.com/ansible/latest/installation_guide/)
- **Docker** v20+ - [Install](https://docs.docker.com/get-docker/)
- **AWS CLI** v2+ - [Install](https://aws.amazon.com/cli/)

### Optional Tools

- **tflint** - Terraform linter
- **yamllint** - YAML linter
- **ansible-lint** - Ansible linter

## Quick Start

### 1. Local Development

```bash
# Start local environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop environment
docker-compose down
```

### 2. Terraform Deployment

```bash
# Navigate to terraform directory
cd terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit configuration with your values
vi terraform.tfvars

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=plan.out

# Apply changes
terraform apply plan.out
```

### 3. Kubernetes Deployment

See [kubernetes/README.md](kubernetes/README.md) for detailed instructions.

### 4. Ansible Configuration

See [ansible/README.md](ansible/README.md) for detailed instructions.

## Validation Commands

### Terraform

```bash
cd terraform

# Format code
terraform fmt -recursive

# Validate syntax
terraform validate

# Security scan (if tfsec installed)
tfsec .

# Lint (if tflint installed)
tflint --recursive
```

### Kubernetes

```bash
cd kubernetes

# Validate YAML
yamllint base/*.yaml

# Dry-run
kubectl apply --dry-run=client -f base/

# Validate with kubeval (if installed)
kubeval base/*.yaml
```

### Ansible

```bash
cd ansible

# Lint playbooks
ansible-lint playbooks/main.yml

# Syntax check
ansible-playbook playbooks/main.yml --syntax-check

# Dry run
ansible-playbook -i inventory/hosts.yml playbooks/main.yml --check
```

## Security Best Practices

### 1. Secrets Management

- **Never** commit secrets to version control
- Use AWS Secrets Manager for production secrets
- Use `.example` files for configuration templates
- Enable GitHub secret scanning

### 2. Terraform State

- Store state in S3 with encryption
- Enable state locking with DynamoDB
- Use separate state files per environment
- Restrict state file access

### 3. Access Control

- Use least-privilege IAM policies
- Enable MFA for production access
- Rotate credentials regularly
- Use service accounts for automation

### 4. Network Security

- Deploy in private subnets
- Use security groups strictly
- Enable VPC Flow Logs
- Implement WAF rules

## Environment Variables

```bash
# AWS Credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Terraform Variables (alternative to .tfvars)
export TF_VAR_db_password="your-secure-password"
export TF_VAR_environment="dev"

# Ansible Vault Password
export ANSIBLE_VAULT_PASSWORD_FILE="~/.vault_pass"
```

## CI/CD Integration

The `ci-cd/ci-cd.yml` file defines the automated deployment pipeline. Key stages:

1. **Validation** - Lint and validate all code
2. **Security Scan** - Check for vulnerabilities
3. **Plan** - Terraform plan for review
4. **Apply** - Deploy infrastructure (manual approval)
5. **Test** - Run integration tests

## Monitoring and Logging

- **CloudWatch** - AWS resource monitoring
- **VPC Flow Logs** - Network traffic analysis
- **CloudTrail** - API call auditing
- **Application Logs** - Container and application logs

## Cost Optimization

- Use reserved instances for production
- Enable auto-scaling for compute
- Set up budget alerts
- Review and terminate unused resources
- Use spot instances for non-critical workloads

## Troubleshooting

### Terraform Issues

```bash
# Refresh state
terraform refresh

# Import existing resource
terraform import aws_instance.example i-1234567890

# Force unlock state
terraform force-unlock <LOCK_ID>

# Debug mode
TF_LOG=DEBUG terraform apply
```

### Kubernetes Issues

```bash
# Check pod status
kubectl get pods -A

# View pod logs
kubectl logs <pod-name>

# Describe resource
kubectl describe pod <pod-name>

# Execute in pod
kubectl exec -it <pod-name> -- /bin/bash
```

### Ansible Issues

```bash
# Verbose output
ansible-playbook playbooks/main.yml -vvv

# Check variables
ansible -i inventory/hosts.yml all -m debug -a "var=hostvars"

# Test connection
ansible all -i inventory/hosts.yml -m ping
```

## Contributing

1. Create feature branch from `main`
2. Make changes following best practices
3. Run all validation commands
4. Submit pull request with clear description
5. Ensure CI/CD pipeline passes

## License

Proprietary - All rights reserved
