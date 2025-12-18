# Enhanced Compute Module Outputs for Financial Services

# Auto Scaling Group
output "autoscaling_group_id" {
  description = "ID of the Auto Scaling Group"
  value       = aws_autoscaling_group.main.id
}

output "autoscaling_group_arn" {
  description = "ARN of the Auto Scaling Group"
  value       = aws_autoscaling_group.main.arn
}

output "autoscaling_group_name" {
  description = "Name of the Auto Scaling Group"
  value       = aws_autoscaling_group.main.name
}

output "autoscaling_group_min_size" {
  description = "Minimum size of the Auto Scaling Group"
  value       = aws_autoscaling_group.main.min_size
}

output "autoscaling_group_max_size" {
  description = "Maximum size of the Auto Scaling Group"
  value       = aws_autoscaling_group.main.max_size
}

output "autoscaling_group_desired_capacity" {
  description = "Desired capacity of the Auto Scaling Group"
  value       = aws_autoscaling_group.main.desired_capacity
}

# Launch Template
output "launch_template_id" {
  description = "ID of the Launch Template"
  value       = aws_launch_template.main.id
}

output "launch_template_arn" {
  description = "ARN of the Launch Template"
  value       = aws_launch_template.main.arn
}

output "launch_template_latest_version" {
  description = "Latest version of the Launch Template"
  value       = aws_launch_template.main.latest_version
}

# Application Load Balancer
output "alb_id" {
  description = "ID of the Application Load Balancer"
  value       = aws_lb.main.id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "alb_hosted_zone_id" {
  description = "Hosted zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

# Target Group
output "target_group_id" {
  description = "ID of the Target Group"
  value       = aws_lb_target_group.main.id
}

output "target_group_arn" {
  description = "ARN of the Target Group"
  value       = aws_lb_target_group.main.arn
}

output "target_group_name" {
  description = "Name of the Target Group"
  value       = aws_lb_target_group.main.name
}

# Listeners
output "https_listener_arn" {
  description = "ARN of the HTTPS listener"
  value       = aws_lb_listener.https.arn
}

output "http_redirect_listener_arn" {
  description = "ARN of the HTTP redirect listener"
  value       = aws_lb_listener.http_redirect.arn
}

# Auto Scaling Policies
output "scale_up_policy_arn" {
  description = "ARN of the scale up policy"
  value       = aws_autoscaling_policy.scale_up.arn
}

output "scale_down_policy_arn" {
  description = "ARN of the scale down policy"
  value       = aws_autoscaling_policy.scale_down.arn
}

output "target_tracking_policy_arn" {
  description = "ARN of the target tracking policy"
  value       = aws_autoscaling_policy.target_tracking_cpu.arn
}

# CloudWatch Alarms
output "high_cpu_alarm_arn" {
  description = "ARN of the high CPU alarm"
  value       = aws_cloudwatch_metric_alarm.high_cpu.arn
}

output "low_cpu_alarm_arn" {
  description = "ARN of the low CPU alarm"
  value       = aws_cloudwatch_metric_alarm.low_cpu.arn
}

# IAM Role and Instance Profile
output "iam_role_arn" {
  description = "ARN of the IAM role for EC2 instances"
  value       = aws_iam_role.main.arn
}

output "iam_role_name" {
  description = "Name of the IAM role for EC2 instances"
  value       = aws_iam_role.main.name
}

output "instance_profile_arn" {
  description = "ARN of the IAM instance profile"
  value       = aws_iam_instance_profile.main.arn
}

output "instance_profile_name" {
  description = "Name of the IAM instance profile"
  value       = aws_iam_instance_profile.main.name
}

# CloudWatch Log Group
output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app_logs.arn
}

# SSM Parameters
output "ssm_parameter_arns" {
  description = "ARNs of SSM parameters"
  value       = { for k, v in aws_ssm_parameter.app_config : k => v.arn }
}

output "ssm_parameter_names" {
  description = "Names of SSM parameters"
  value       = { for k, v in aws_ssm_parameter.app_config : k => v.name }
}

# WAF Association
output "waf_association_id" {
  description = "ID of the WAF association"
  value       = var.waf_web_acl_arn != "" ? aws_wafv2_web_acl_association.main[0].id : null
}

# Scheduled Actions
output "scale_down_schedule_arn" {
  description = "ARN of the scale down scheduled action"
  value       = var.enable_scheduled_scaling && var.environment != "prod" ? aws_autoscaling_schedule.scale_down_evening[0].arn : null
}

output "scale_up_schedule_arn" {
  description = "ARN of the scale up scheduled action"
  value       = var.enable_scheduled_scaling && var.environment != "prod" ? aws_autoscaling_schedule.scale_up_morning[0].arn : null
}

# Configuration Summary
output "compute_configuration" {
  description = "Summary of compute configuration"
  value = {
    instance_type         = var.instance_type
    min_size              = var.min_size
    max_size              = var.max_size
    desired_capacity      = var.desired_capacity
    auto_scaling_enabled  = true
    load_balancer_enabled = true
    ssl_enabled           = true
    health_checks_enabled = true
    monitoring_enabled    = true
  }
}

# Security Configuration
output "security_configuration" {
  description = "Summary of security configuration"
  value = {
    encryption_at_rest    = true
    encryption_in_transit = true
    iam_roles_enabled     = true
    security_groups       = [var.security_group_id, var.alb_security_group_id]
    waf_enabled           = var.waf_web_acl_arn != ""
    ssl_certificate       = var.ssl_certificate_arn
    access_logs_enabled   = true
  }
}

# Monitoring Configuration
output "monitoring_configuration" {
  description = "Summary of monitoring configuration"
  value = {
    cloudwatch_logs_enabled    = true
    cloudwatch_metrics_enabled = true
    auto_scaling_alarms        = true
    health_checks_enabled      = true
    log_retention_days         = var.log_retention_days
    custom_metrics_enabled     = true
  }
}

# Cost Optimization
output "cost_optimization_features" {
  description = "Summary of cost optimization features"
  value = {
    scheduled_scaling_enabled = var.enable_scheduled_scaling
    auto_scaling_enabled      = true
    instance_right_sizing     = true
    storage_optimization      = true
    monitoring_cost_control   = true
  }
}

# High Availability
output "high_availability_configuration" {
  description = "Summary of high availability configuration"
  value = {
    multi_az_deployment   = length(var.private_subnet_ids) > 1
    auto_scaling_enabled  = true
    load_balancer_enabled = true
    health_checks_enabled = true
    automatic_failover    = true
    instance_replacement  = true
  }
}

# Application Configuration
output "application_endpoints" {
  description = "Application endpoint information"
  value = {
    load_balancer_dns = aws_lb.main.dns_name
    https_endpoint    = "https://${aws_lb.main.dns_name}"
    health_check_url  = "https://${aws_lb.main.dns_name}${var.health_check_path}"
    application_port  = var.app_port
  }
  sensitive = false
}

# Resource Tags
output "resource_tags" {
  description = "Tags applied to compute resources"
  value       = var.common_tags
}
