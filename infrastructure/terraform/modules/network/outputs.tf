# Enhanced Network Module Outputs for Financial Services

# VPC
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_arn" {
  description = "ARN of the VPC"
  value       = aws_vpc.main.arn
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "vpc_default_security_group_id" {
  description = "ID of the default security group"
  value       = aws_vpc.main.default_security_group_id
}

output "vpc_default_network_acl_id" {
  description = "ID of the default network ACL"
  value       = aws_vpc.main.default_network_acl_id
}

output "vpc_default_route_table_id" {
  description = "ID of the default route table"
  value       = aws_vpc.main.default_route_table_id
}

# Internet Gateway
output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "internet_gateway_arn" {
  description = "ARN of the Internet Gateway"
  value       = aws_internet_gateway.main.arn
}

# Public Subnets
output "public_subnet_ids" {
  description = "List of IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "public_subnet_arns" {
  description = "List of ARNs of the public subnets"
  value       = aws_subnet.public[*].arn
}

output "public_subnet_cidr_blocks" {
  description = "List of CIDR blocks of the public subnets"
  value       = aws_subnet.public[*].cidr_block
}

output "public_subnet_availability_zones" {
  description = "List of availability zones of the public subnets"
  value       = aws_subnet.public[*].availability_zone
}

# Private Subnets
output "private_subnet_ids" {
  description = "List of IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "private_subnet_arns" {
  description = "List of ARNs of the private subnets"
  value       = aws_subnet.private[*].arn
}

output "private_subnet_cidr_blocks" {
  description = "List of CIDR blocks of the private subnets"
  value       = aws_subnet.private[*].cidr_block
}

output "private_subnet_availability_zones" {
  description = "List of availability zones of the private subnets"
  value       = aws_subnet.private[*].availability_zone
}

# Database Subnets
output "database_subnet_ids" {
  description = "List of IDs of the database subnets"
  value       = aws_subnet.database[*].id
}

output "database_subnet_arns" {
  description = "List of ARNs of the database subnets"
  value       = aws_subnet.database[*].arn
}

output "database_subnet_cidr_blocks" {
  description = "List of CIDR blocks of the database subnets"
  value       = aws_subnet.database[*].cidr_block
}

output "database_subnet_availability_zones" {
  description = "List of availability zones of the database subnets"
  value       = aws_subnet.database[*].availability_zone
}

# NAT Gateways
output "nat_gateway_ids" {
  description = "List of IDs of the NAT Gateways"
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_public_ips" {
  description = "List of public IP addresses of the NAT Gateways"
  value       = aws_nat_gateway.main[*].public_ip
}

output "elastic_ip_ids" {
  description = "List of IDs of the Elastic IPs for NAT Gateways"
  value       = aws_eip.nat[*].id
}

output "elastic_ip_public_ips" {
  description = "List of public IP addresses of the Elastic IPs"
  value       = aws_eip.nat[*].public_ip
}

# Route Tables
output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "List of IDs of the private route tables"
  value       = aws_route_table.private[*].id
}

output "database_route_table_id" {
  description = "ID of the database route table"
  value       = aws_route_table.database.id
}

# VPC Endpoints
output "vpc_endpoint_s3_id" {
  description = "ID of the S3 VPC endpoint"
  value       = aws_vpc_endpoint.s3.id
}

output "vpc_endpoint_dynamodb_id" {
  description = "ID of the DynamoDB VPC endpoint"
  value       = aws_vpc_endpoint.dynamodb.id
}

output "vpc_endpoint_ec2_id" {
  description = "ID of the EC2 VPC endpoint"
  value       = aws_vpc_endpoint.ec2.id
}

output "vpc_endpoint_ssm_id" {
  description = "ID of the SSM VPC endpoint"
  value       = aws_vpc_endpoint.ssm.id
}

output "vpc_endpoint_logs_id" {
  description = "ID of the CloudWatch Logs VPC endpoint"
  value       = aws_vpc_endpoint.logs.id
}

output "vpc_endpoint_monitoring_id" {
  description = "ID of the CloudWatch Monitoring VPC endpoint"
  value       = aws_vpc_endpoint.monitoring.id
}

# Security Groups
output "vpc_endpoints_security_group_id" {
  description = "ID of the VPC endpoints security group"
  value       = aws_security_group.vpc_endpoints.id
}

# Network ACLs
output "public_network_acl_id" {
  description = "ID of the public network ACL"
  value       = aws_network_acl.public.id
}

output "private_network_acl_id" {
  description = "ID of the private network ACL"
  value       = aws_network_acl.private.id
}

output "database_network_acl_id" {
  description = "ID of the database network ACL"
  value       = aws_network_acl.database.id
}

# VPC Flow Logs
output "vpc_flow_log_id" {
  description = "ID of the VPC Flow Log"
  value       = aws_flow_log.vpc.id
}

output "vpc_flow_log_group_name" {
  description = "Name of the VPC Flow Log CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.vpc_flow_log.name
}

output "vpc_flow_log_group_arn" {
  description = "ARN of the VPC Flow Log CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.vpc_flow_log.arn
}

output "flow_log_role_arn" {
  description = "ARN of the VPC Flow Log IAM role"
  value       = aws_iam_role.flow_log.arn
}

# Transit Gateway (if enabled)
output "transit_gateway_id" {
  description = "ID of the Transit Gateway"
  value       = var.enable_transit_gateway ? aws_ec2_transit_gateway.main[0].id : null
}

output "transit_gateway_arn" {
  description = "ARN of the Transit Gateway"
  value       = var.enable_transit_gateway ? aws_ec2_transit_gateway.main[0].arn : null
}

output "transit_gateway_vpc_attachment_id" {
  description = "ID of the Transit Gateway VPC attachment"
  value       = var.enable_transit_gateway ? aws_ec2_transit_gateway_vpc_attachment.main[0].id : null
}

# VPN (if enabled)
output "customer_gateway_id" {
  description = "ID of the Customer Gateway"
  value       = var.enable_vpn ? aws_customer_gateway.main[0].id : null
}

output "vpn_gateway_id" {
  description = "ID of the VPN Gateway"
  value       = var.enable_vpn ? aws_vpn_gateway.main[0].id : null
}

output "vpn_connection_id" {
  description = "ID of the VPN Connection"
  value       = var.enable_vpn ? aws_vpn_connection.main[0].id : null
}

# Direct Connect (if enabled)
output "direct_connect_gateway_id" {
  description = "ID of the Direct Connect Gateway"
  value       = var.enable_direct_connect ? aws_dx_gateway.main[0].id : null
}

# Network Configuration Summary
output "network_configuration" {
  description = "Summary of network configuration"
  value = {
    vpc_cidr                = aws_vpc.main.cidr_block
    availability_zones      = data.aws_availability_zones.available.names
    public_subnets_count   = length(aws_subnet.public)
    private_subnets_count  = length(aws_subnet.private)
    database_subnets_count = length(aws_subnet.database)
    nat_gateways_count     = length(aws_nat_gateway.main)
    vpc_endpoints_enabled  = var.enable_vpc_endpoints
    flow_logs_enabled      = var.enable_flow_logs
    multi_az_deployment    = var.multi_az_deployment
  }
}

# Security Configuration Summary
output "security_configuration" {
  description = "Summary of security configuration"
  value = {
    network_acls_enabled      = var.enable_network_acls
    security_groups_enabled   = var.enable_security_groups
    vpc_flow_logs_enabled    = var.enable_flow_logs
    vpc_endpoints_enabled    = var.enable_vpc_endpoints
    private_subnets_isolated = true
    database_subnets_isolated = true
    encryption_in_transit    = true
  }
}

# High Availability Summary
output "high_availability_configuration" {
  description = "Summary of high availability configuration"
  value = {
    multi_az_deployment       = var.multi_az_deployment
    availability_zones_count  = length(data.aws_availability_zones.available.names)
    redundant_nat_gateways   = var.nat_gateway_per_az
    cross_zone_load_balancing = var.cross_zone_load_balancing
    disaster_recovery_enabled = var.enable_disaster_recovery
    backup_region            = var.backup_region
  }
}

# Compliance Summary
output "compliance_configuration" {
  description = "Summary of compliance configuration"
  value = {
    compliance_standards        = var.compliance_standards
    compliance_monitoring       = var.enable_compliance_monitoring
    data_residency_restrictions = var.data_residency_requirements.restrict_cross_border
    allowed_regions            = var.data_residency_requirements.allowed_regions
    encryption_required        = var.data_residency_requirements.encryption_required
    audit_logging_enabled      = var.enable_flow_logs
  }
}

# Cost Optimization Summary
output "cost_optimization_configuration" {
  description = "Summary of cost optimization configuration"
  value = {
    cost_optimization_enabled = var.enable_cost_optimization
    single_nat_gateway       = var.single_nat_gateway
    vpc_endpoints_enabled    = var.enable_vpc_endpoints
    enhanced_networking      = var.enhanced_networking
    placement_group_strategy = var.placement_group_strategy
  }
}

# Connectivity Options
output "connectivity_options" {
  description = "Summary of connectivity options"
  value = {
    internet_gateway_enabled  = true
    nat_gateway_enabled      = var.enable_nat_gateway
    vpn_enabled             = var.enable_vpn
    direct_connect_enabled  = var.enable_direct_connect
    transit_gateway_enabled = var.enable_transit_gateway
    vpc_peering_ready       = true
  }
}

# DNS Configuration
output "dns_configuration" {
  description = "Summary of DNS configuration"
  value = {
    dns_hostnames_enabled = var.enable_dns_hostnames
    dns_support_enabled   = var.enable_dns_support
    private_dns_enabled   = true
    route53_integration   = true
  }
}

# Monitoring Configuration
output "monitoring_configuration" {
  description = "Summary of monitoring configuration"
  value = {
    vpc_flow_logs_enabled     = var.enable_flow_logs
    network_monitoring_enabled = var.enable_network_monitoring
    traffic_mirroring_enabled = var.enable_traffic_mirroring
    network_insights_enabled  = var.network_insights_enabled
    cloudwatch_integration   = true
  }
}

# Resource Tags
output "resource_tags" {
  description = "Tags applied to network resources"
  value       = var.common_tags
}
