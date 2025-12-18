# Ansible Configuration Management

## Prerequisites

- Ansible 2.10+
- SSH access to target hosts
- Python 3 on target hosts

## Setup

### 1. Configure Inventory

```bash
# Copy example inventory
cp inventory/hosts.example.yml inventory/hosts.yml

# Edit with your actual hosts
vi inventory/hosts.yml
```

### 2. Configure Vault for Secrets

```bash
# Create vault file
ansible-vault create group_vars/all/vault.yml

# Add sensitive variables:
---
db_root_password: "your-secure-password"
db_app_password: "your-app-password"
```

### 3. Test Connectivity

```bash
# Ping all hosts
ansible all -i inventory/hosts.yml -m ping

# Check Python installation
ansible all -i inventory/hosts.yml -m command -a "python3 --version"
```

## Running Playbooks

### Dry Run (Check Mode)

```bash
ansible-playbook -i inventory/hosts.yml playbooks/main.yml --check
```

### Execute Playbook

```bash
# With vault password
ansible-playbook -i inventory/hosts.yml playbooks/main.yml --ask-vault-pass

# Or use password file
ansible-playbook -i inventory/hosts.yml playbooks/main.yml --vault-password-file ~/.vault_pass
```

### Run Specific Roles

```bash
# Only webserver configuration
ansible-playbook -i inventory/hosts.yml playbooks/main.yml --tags webserver

# Only database configuration
ansible-playbook -i inventory/hosts.yml playbooks/main.yml --tags database
```

## Linting

```bash
# Lint all playbooks
ansible-lint playbooks/main.yml

# Lint with specific rules
ansible-lint -r rules/ playbooks/
```

## Best Practices

1. **Never commit plain-text passwords**
   - Use ansible-vault for all sensitive data
   - Store vault password securely

2. **Use roles for reusability**
   - Keep roles focused and modular
   - Use role dependencies appropriately

3. **Test in development first**
   - Always use --check mode first
   - Test on dev environment before production

4. **Tag your tasks**
   - Use tags for selective execution
   - Document tag usage in README

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH connection
ssh -i ~/.ssh/key.pem ubuntu@host

# Check SSH config
ansible all -i inventory/hosts.yml -m ping -vvv
```

### Vault Password Issues

```bash
# Re-encrypt vault file
ansible-vault rekey group_vars/all/vault.yml

# Edit encrypted file
ansible-vault edit group_vars/all/vault.yml
```

### Permission Denied

```bash
# Run with sudo
ansible-playbook -i inventory/hosts.yml playbooks/main.yml --become --ask-become-pass
```
