# Enhanced Network Module Variables for Financial Services

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

# Subnet Configuration
variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
  validation {
    condition     = length(var.public_subnet_cidrs) >= 2
    error_message = "At least 2 public subnets are required for high availability."
  }
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
  validation {
    condition     = length(var.private_subnet_cidrs) >= 2
    error_message = "At least 2 private subnets are required for high availability."
  }
}

variable "database_subnet_cidrs" {
  description = "List of CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.100.0/24", "10.0.200.0/24"]
  validation {
    condition     = length(var.database_subnet_cidrs) >= 2
    error_message = "At least 2 database subnets are required for high availability."
  }
}

# NAT Gateway Configuration
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use a single NAT Gateway for all private subnets"
  type        = bool
  default     = false
}

# VPC Endpoints Configuration
variable "enable_vpc_endpoints" {
  description = "Enable VPC endpoints for AWS services"
  type        = bool
  default     = true
}

variable "vpc_endpoint_services" {
  description = "List of AWS services to create VPC endpoints for"
  type        = list(string)
  default     = ["s3", "dynamodb", "ec2", "ssm", "ssmmessages", "ec2messages", "logs", "monitoring"]
}

# Network Security Configuration
variable "admin_cidr_block" {
  description = "CIDR block for administrative access"
  type        = string
  default     = "10.0.0.0/8"
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

variable "flow_log_retention_days" {
  description = "VPC Flow Log retention in days"
  type        = number
  default     = 30
  validation {
    condition     = var.flow_log_retention_days >= 1 && var.flow_log_retention_days <= 3653
    error_message = "Flow log retention must be between 1 and 3653 days."
  }
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

# Transit Gateway Configuration
variable "enable_transit_gateway" {
  description = "Enable Transit Gateway for multi-VPC connectivity"
  type        = bool
  default     = false
}

variable "transit_gateway_asn" {
  description = "ASN for Transit Gateway"
  type        = number
  default     = 64512
}

# VPN Configuration
variable "enable_vpn" {
  description = "Enable Site-to-Site VPN"
  type        = bool
  default     = false
}

variable "customer_gateway_ip" {
  description = "IP address of customer gateway for VPN"
  type        = string
  default     = ""
}

variable "customer_gateway_bgp_asn" {
  description = "BGP ASN of customer gateway"
  type        = number
  default     = 65000
}

# Direct Connect Configuration
variable "enable_direct_connect" {
  description = "Enable Direct Connect Gateway"
  type        = bool
  default     = false
}

variable "direct_connect_asn" {
  description = "ASN for Direct Connect Gateway"
  type        = number
  default     = 64512
}

# DNS Configuration
variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

# Network Monitoring
variable "enable_network_monitoring" {
  description = "Enable comprehensive network monitoring"
  type        = bool
  default     = true
}

variable "enable_traffic_mirroring" {
  description = "Enable VPC Traffic Mirroring"
  type        = bool
  default     = false
}

# Security Configuration
variable "enable_network_acls" {
  description = "Enable custom Network ACLs"
  type        = bool
  default     = true
}

variable "enable_security_groups" {
  description = "Enable custom Security Groups"
  type        = bool
  default     = true
}

variable "allowed_ssh_cidrs" {
  description = "List of CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = []
}

variable "allowed_http_cidrs" {
  description = "List of CIDR blocks allowed for HTTP access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "allowed_https_cidrs" {
  description = "List of CIDR blocks allowed for HTTPS access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# High Availability Configuration
variable "multi_az_deployment" {
  description = "Deploy resources across multiple Availability Zones"
  type        = bool
  default     = true
}

variable "cross_zone_load_balancing" {
  description = "Enable cross-zone load balancing"
  type        = bool
  default     = true
}

# Cost Optimization
variable "enable_cost_optimization" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

variable "nat_gateway_per_az" {
  description = "Create NAT Gateway per Availability Zone"
  type        = bool
  default     = true
}

# Compliance Configuration
variable "compliance_standards" {
  description = "List of compliance standards to meet"
  type        = list(string)
  default     = ["PCI-DSS", "SOX", "GDPR", "ISO-27001"]
}

variable "enable_compliance_monitoring" {
  description = "Enable compliance monitoring"
  type        = bool
  default     = true
}

variable "data_residency_requirements" {
  description = "Data residency requirements"
  type = object({
    restrict_cross_border = bool
    allowed_regions       = list(string)
    encryption_required   = bool
  })
  default = {
    restrict_cross_border = true
    allowed_regions       = ["us-east-1", "us-west-2"]
    encryption_required   = true
  }
}

# Network Performance
variable "enhanced_networking" {
  description = "Enable enhanced networking features"
  type        = bool
  default     = true
}

variable "placement_group_strategy" {
  description = "Placement group strategy for instances"
  type        = string
  default     = "cluster"
  validation {
    condition     = contains(["cluster", "partition", "spread"], var.placement_group_strategy)
    error_message = "Placement group strategy must be one of: cluster, partition, spread."
  }
}

# Disaster Recovery
variable "enable_disaster_recovery" {
  description = "Enable disaster recovery configuration"
  type        = bool
  default     = true
}

variable "backup_region" {
  description = "Backup region for disaster recovery"
  type        = string
  default     = "us-west-2"
}

variable "cross_region_replication" {
  description = "Enable cross-region replication"
  type        = bool
  default     = false
}

# Common Tags
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project    = "quantis"
    ManagedBy  = "terraform"
    Compliance = "financial-grade"
    DataClass  = "confidential"
  }
}

# Advanced Network Configuration
variable "custom_route_tables" {
  description = "Custom route table configurations"
  type = map(object({
    subnet_type = string
    routes = list(object({
      cidr_block = string
      gateway_id = string
    }))
  }))
  default = {}
}

variable "network_insights_enabled" {
  description = "Enable VPC Network Insights"
  type        = bool
  default     = true
}

variable "ipv6_enabled" {
  description = "Enable IPv6 support"
  type        = bool
  default     = false
}

# Security Hardening
variable "security_hardening" {
  description = "Security hardening configuration"
  type = object({
    disable_api_termination    = bool
    enable_detailed_monitoring = bool
    enable_ebs_optimization    = bool
    enable_source_dest_check   = bool
  })
  default = {
    disable_api_termination    = true
    enable_detailed_monitoring = true
    enable_ebs_optimization    = true
    enable_source_dest_check   = false
  }
}
