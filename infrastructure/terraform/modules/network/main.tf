# Enhanced Network Module for Financial Services
# Implements robust network infrastructure with security, compliance, and high availability

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vpc"
    Environment = var.environment
    Purpose     = "main-network"
    Compliance  = "financial-grade"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-igw"
    Environment = var.environment
    Purpose     = "internet-gateway"
    Compliance  = "financial-grade"
  })
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-public-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "public"
    Purpose     = "public-network"
    Compliance  = "financial-grade"
    AZ          = data.aws_availability_zones.available.names[count.index]
  })
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-private-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "private"
    Purpose     = "private-network"
    Compliance  = "financial-grade"
    AZ          = data.aws_availability_zones.available.names[count.index]
  })
}

# Database Subnets
resource "aws_subnet" "database" {
  count = length(var.database_subnet_cidrs)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.database_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-database-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "database"
    Purpose     = "database-network"
    Compliance  = "financial-grade"
    AZ          = data.aws_availability_zones.available.names[count.index]
  })
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? length(var.public_subnet_cidrs) : 0

  domain = "vpc"
  depends_on = [aws_internet_gateway.main]

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-nat-eip-${count.index + 1}"
    Environment = var.environment
    Purpose     = "nat-gateway"
    Compliance  = "financial-grade"
  })
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? length(var.public_subnet_cidrs) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-nat-gateway-${count.index + 1}"
    Environment = var.environment
    Purpose     = "nat-gateway"
    Compliance  = "financial-grade"
  })

  depends_on = [aws_internet_gateway.main]
}

# Route Tables - Public
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-public-rt"
    Environment = var.environment
    Type        = "public"
    Purpose     = "public-routing"
    Compliance  = "financial-grade"
  })
}

# Route Tables - Private
resource "aws_route_table" "private" {
  count = var.enable_nat_gateway ? length(var.private_subnet_cidrs) : 1

  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[count.index].id
    }
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-private-rt-${count.index + 1}"
    Environment = var.environment
    Type        = "private"
    Purpose     = "private-routing"
    Compliance  = "financial-grade"
  })
}

# Route Tables - Database
resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-database-rt"
    Environment = var.environment
    Type        = "database"
    Purpose     = "database-routing"
    Compliance  = "financial-grade"
  })
}

# Route Table Associations - Public
resource "aws_route_table_association" "public" {
  count = length(var.public_subnet_cidrs)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route Table Associations - Private
resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = var.enable_nat_gateway ? aws_route_table.private[count.index].id : aws_route_table.private[0].id
}

# Route Table Associations - Database
resource "aws_route_table_association" "database" {
  count = length(var.database_subnet_cidrs)

  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.database.id
}

# VPC Endpoints for AWS Services
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"
  
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-s3-endpoint"
    Environment = var.environment
    Purpose     = "s3-access"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.dynamodb"
  
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-dynamodb-endpoint"
    Environment = var.environment
    Purpose     = "dynamodb-access"
    Compliance  = "financial-grade"
  })
}

# Interface VPC Endpoints
resource "aws_vpc_endpoint" "ec2" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ec2"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeImages",
          "ec2:DescribeSnapshots"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-ec2-endpoint"
    Environment = var.environment
    Purpose     = "ec2-access"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ssm"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-ssm-endpoint"
    Environment = var.environment
    Purpose     = "ssm-access"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpc_endpoint" "ssm_messages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ssmmessages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-ssm-messages-endpoint"
    Environment = var.environment
    Purpose     = "ssm-messages-access"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpc_endpoint" "ec2_messages" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ec2messages"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-ec2-messages-endpoint"
    Environment = var.environment
    Purpose     = "ec2-messages-access"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-logs-endpoint"
    Environment = var.environment
    Purpose     = "cloudwatch-logs-access"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpc_endpoint" "monitoring" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.monitoring"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  
  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-monitoring-endpoint"
    Environment = var.environment
    Purpose     = "cloudwatch-monitoring-access"
    Compliance  = "financial-grade"
  })
}

# Security Group for VPC Endpoints
resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.app_name}-${var.environment}-vpc-endpoints-sg"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vpc-endpoints-sg"
    Environment = var.environment
    Purpose     = "vpc-endpoints-security"
    Compliance  = "financial-grade"
  })
}

# Network ACLs for additional security
resource "aws_network_acl" "public" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.public[*].id

  # Allow inbound HTTP
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }

  # Allow inbound HTTPS
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Allow inbound SSH from admin networks
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = var.admin_cidr_block
    from_port  = 22
    to_port    = 22
  }

  # Allow return traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 130
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Allow all outbound traffic
  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-public-nacl"
    Environment = var.environment
    Type        = "public"
    Purpose     = "network-security"
    Compliance  = "financial-grade"
  })
}

resource "aws_network_acl" "private" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.private[*].id

  # Allow inbound from VPC
  ingress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 0
    to_port    = 0
  }

  # Allow return traffic
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  # Allow outbound HTTPS
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }

  # Allow outbound to VPC
  egress {
    protocol   = "-1"
    rule_no    = 110
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 0
    to_port    = 0
  }

  # Allow outbound DNS
  egress {
    protocol   = "udp"
    rule_no    = 120
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 53
    to_port    = 53
  }

  # Allow outbound NTP
  egress {
    protocol   = "udp"
    rule_no    = 130
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 123
    to_port    = 123
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-private-nacl"
    Environment = var.environment
    Type        = "private"
    Purpose     = "network-security"
    Compliance  = "financial-grade"
  })
}

resource "aws_network_acl" "database" {
  vpc_id     = aws_vpc.main.id
  subnet_ids = aws_subnet.database[*].id

  # Allow inbound from private subnets only
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = var.private_subnet_cidrs[0]
    from_port  = 3306
    to_port    = 3306
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = var.private_subnet_cidrs[1]
    from_port  = 3306
    to_port    = 3306
  }

  # Allow PostgreSQL
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = var.private_subnet_cidrs[0]
    from_port  = 5432
    to_port    = 5432
  }

  ingress {
    protocol   = "tcp"
    rule_no    = 130
    action     = "allow"
    cidr_block = var.private_subnet_cidrs[1]
    from_port  = 5432
    to_port    = 5432
  }

  # Allow return traffic
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-database-nacl"
    Environment = var.environment
    Type        = "database"
    Purpose     = "database-security"
    Compliance  = "financial-grade"
  })
}

# VPC Flow Logs
resource "aws_flow_log" "vpc" {
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vpc-flow-log"
    Environment = var.environment
    Purpose     = "network-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_cloudwatch_log_group" "vpc_flow_log" {
  name              = "/aws/vpc/${var.app_name}-${var.environment}-flow-log"
  retention_in_days = var.flow_log_retention_days
  kms_key_id        = var.kms_key_id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vpc-flow-log-group"
    Environment = var.environment
    Purpose     = "network-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_iam_role" "flow_log" {
  name = "${var.app_name}-${var.environment}-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-flow-log-role"
    Environment = var.environment
    Purpose     = "network-monitoring"
    Compliance  = "financial-grade"
  })
}

resource "aws_iam_role_policy" "flow_log" {
  name = "${var.app_name}-${var.environment}-flow-log-policy"
  role = aws_iam_role.flow_log.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Transit Gateway (for multi-VPC connectivity)
resource "aws_ec2_transit_gateway" "main" {
  count = var.enable_transit_gateway ? 1 : 0

  description                     = "Transit Gateway for ${var.app_name} ${var.environment}"
  default_route_table_association = "enable"
  default_route_table_propagation = "enable"
  dns_support                     = "enable"
  vpn_ecmp_support               = "enable"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-tgw"
    Environment = var.environment
    Purpose     = "multi-vpc-connectivity"
    Compliance  = "financial-grade"
  })
}

resource "aws_ec2_transit_gateway_vpc_attachment" "main" {
  count = var.enable_transit_gateway ? 1 : 0

  subnet_ids         = aws_subnet.private[*].id
  transit_gateway_id = aws_ec2_transit_gateway.main[0].id
  vpc_id             = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-tgw-attachment"
    Environment = var.environment
    Purpose     = "vpc-attachment"
    Compliance  = "financial-grade"
  })
}

# Customer Gateway and VPN (for hybrid connectivity)
resource "aws_customer_gateway" "main" {
  count = var.enable_vpn ? 1 : 0

  bgp_asn    = var.customer_gateway_bgp_asn
  ip_address = var.customer_gateway_ip
  type       = "ipsec.1"

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-cgw"
    Environment = var.environment
    Purpose     = "hybrid-connectivity"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpn_gateway" "main" {
  count = var.enable_vpn ? 1 : 0

  vpc_id = aws_vpc.main.id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vgw"
    Environment = var.environment
    Purpose     = "vpn-gateway"
    Compliance  = "financial-grade"
  })
}

resource "aws_vpn_connection" "main" {
  count = var.enable_vpn ? 1 : 0

  customer_gateway_id = aws_customer_gateway.main[0].id
  type                = "ipsec.1"
  vpn_gateway_id      = aws_vpn_gateway.main[0].id
  static_routes_only  = true

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-vpn"
    Environment = var.environment
    Purpose     = "site-to-site-vpn"
    Compliance  = "financial-grade"
  })
}

# Direct Connect Gateway (for dedicated connectivity)
resource "aws_dx_gateway" "main" {
  count = var.enable_direct_connect ? 1 : 0

  name           = "${var.app_name}-${var.environment}-dxgw"
  amazon_side_asn = var.direct_connect_asn

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-dxgw"
    Environment = var.environment
    Purpose     = "direct-connect"
    Compliance  = "financial-grade"
  })
}

