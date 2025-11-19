# Enhanced Compute Module Variables for Financial Services

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

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for instances"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for load balancer"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for instances"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security group ID for Application Load Balancer"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN for encryption"
  type        = string
}

# Instance Configuration
variable "ami_id" {
  description = "AMI ID for instances (leave empty for latest Amazon Linux 2)"
  type        = string
  default     = ""
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_pair_name" {
  description = "Name of the EC2 Key Pair"
  type        = string
  default     = ""
}

# Storage Configuration
variable "root_volume_type" {
  description = "Type of root volume"
  type        = string
  default     = "gp3"
  validation {
    condition     = contains(["gp2", "gp3", "io1", "io2"], var.root_volume_type)
    error_message = "Root volume type must be one of: gp2, gp3, io1, io2."
  }
}

variable "root_volume_size" {
  description = "Size of root volume in GB"
  type        = number
  default     = 20
}

variable "data_volume_type" {
  description = "Type of data volume"
  type        = string
  default     = "gp3"
}

variable "data_volume_size" {
  description = "Size of data volume in GB"
  type        = number
  default     = 100
}

# Auto Scaling Configuration
variable "min_size" {
  description = "Minimum number of instances"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "desired_capacity" {
  description = "Desired number of instances"
  type        = number
  default     = 2
}

variable "health_check_grace_period" {
  description = "Health check grace period in seconds"
  type        = number
  default     = 300
}

variable "instance_warmup" {
  description = "Instance warmup time in seconds"
  type        = number
  default     = 300
}

# Scaling Policies
variable "scale_up_adjustment" {
  description = "Number of instances to add when scaling up"
  type        = number
  default     = 1
}

variable "scale_down_adjustment" {
  description = "Number of instances to remove when scaling down"
  type        = number
  default     = -1
}

variable "scale_up_cooldown" {
  description = "Cooldown period for scale up in seconds"
  type        = number
  default     = 300
}

variable "scale_down_cooldown" {
  description = "Cooldown period for scale down in seconds"
  type        = number
  default     = 300
}

variable "target_cpu_utilization" {
  description = "Target CPU utilization for auto scaling"
  type        = number
  default     = 70
}

# CloudWatch Alarms
variable "high_cpu_threshold" {
  description = "High CPU threshold for scaling up"
  type        = number
  default     = 80
}

variable "low_cpu_threshold" {
  description = "Low CPU threshold for scaling down"
  type        = number
  default     = 20
}

# Application Configuration
variable "app_port" {
  description = "Port on which the application runs"
  type        = number
  default     = 8000
}

variable "health_check_path" {
  description = "Health check path for load balancer"
  type        = string
  default     = "/health"
}

variable "enable_stickiness" {
  description = "Enable session stickiness"
  type        = bool
  default     = false
}

# Load Balancer Configuration
variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate for HTTPS listener"
  type        = string
}

variable "access_logs_bucket" {
  description = "S3 bucket for ALB access logs"
  type        = string
}

variable "waf_web_acl_arn" {
  description = "ARN of WAF Web ACL to associate with ALB"
  type        = string
  default     = ""
}

# Target Group Configuration
variable "target_group_arns" {
  description = "List of target group ARNs for auto scaling group"
  type        = list(string)
  default     = []
}

# IAM Configuration
variable "secrets_manager_arns" {
  description = "List of Secrets Manager ARNs for instance access"
  type        = list(string)
  default     = []
}

variable "app_data_bucket_arn" {
  description = "ARN of S3 bucket for application data"
  type        = string
}

variable "ssm_parameter_path" {
  description = "SSM parameter path for application configuration"
  type        = string
  default     = "/quantis"
}

# Application Parameters
variable "app_parameters" {
  description = "Application configuration parameters"
  type = map(object({
    type        = string
    value       = string
    description = string
  }))
  default = {}
}

# Monitoring Configuration
variable "cloudwatch_config" {
  description = "CloudWatch agent configuration"
  type        = string
  default     = ""
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# Scheduled Scaling
variable "enable_scheduled_scaling" {
  description = "Enable scheduled scaling for cost optimization"
  type        = bool
  default     = false
}

# Common Tags
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "quantis"
    ManagedBy   = "terraform"
    Compliance  = "financial-grade"
    DataClass   = "confidential"
  }
}
