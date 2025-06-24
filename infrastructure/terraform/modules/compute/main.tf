# Enhanced Compute Module for Financial Services
# Implements robust compute infrastructure with auto-scaling, security, and compliance

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# Get the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Launch Template for Auto Scaling Group
resource "aws_launch_template" "main" {
  name_prefix   = "${var.app_name}-${var.environment}-"
  image_id      = var.ami_id != "" ? var.ami_id : data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_pair_name

  vpc_security_group_ids = [var.security_group_id]

  # IAM instance profile
  iam_instance_profile {
    name = aws_iam_instance_profile.main.name
  }

  # EBS optimization
  ebs_optimized = true

  # Block device mappings with encryption
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_type           = var.root_volume_type
      volume_size           = var.root_volume_size
      encrypted             = true
      kms_key_id           = var.kms_key_id
      delete_on_termination = true
    }
  }

  # Additional data volume for application data
  block_device_mappings {
    device_name = "/dev/xvdf"
    ebs {
      volume_type           = var.data_volume_type
      volume_size           = var.data_volume_size
      encrypted             = true
      kms_key_id           = var.kms_key_id
      delete_on_termination = false
    }
  }

  # User data script for instance initialization
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    app_name           = var.app_name
    environment        = var.environment
    cloudwatch_config  = var.cloudwatch_config
    ssm_parameter_path = var.ssm_parameter_path
    s3_bucket         = var.app_data_bucket
    kms_key_id        = var.kms_key_id
  }))

  # Metadata options for enhanced security
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                = "required"  # Require IMDSv2
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  # Monitoring
  monitoring {
    enabled = true
  }

  # Network interfaces
  network_interfaces {
    associate_public_ip_address = false
    security_groups            = [var.security_group_id]
    delete_on_termination      = true
  }

  tag_specifications {
    resource_type = "instance"
    tags = merge(var.common_tags, {
      Name        = "${var.app_name}-${var.environment}-instance"
      Environment = var.environment
      Purpose     = "application-server"
      Compliance  = "financial-grade"
    })
  }

  tag_specifications {
    resource_type = "volume"
    tags = merge(var.common_tags, {
      Name        = "${var.app_name}-${var.environment}-volume"
      Environment = var.environment
      Purpose     = "application-storage"
      Compliance  = "financial-grade"
    })
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-launch-template"
    Environment = var.environment
    Purpose     = "compute-template"
    Compliance  = "financial-grade"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "main" {
  name                = "${var.app_name}-${var.environment}-asg"
  vpc_zone_identifier = var.private_subnet_ids
  target_group_arns   = var.target_group_arns
  health_check_type   = "ELB"
  health_check_grace_period = var.health_check_grace_period

  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.desired_capacity

  # Instance refresh configuration
  instance_refresh {
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 50
      instance_warmup       = var.instance_warmup
    }
    triggers = ["tag"]
  }

  launch_template {
    id      = aws_launch_template.main.id
    version = "$Latest"
  }

  # Termination policies
  termination_policies = ["OldestInstance"]

  # Enable instance protection for production
  protect_from_scale_in = var.environment == "prod"

  # Tags
  dynamic "tag" {
    for_each = merge(var.common_tags, {
      Name        = "${var.app_name}-${var.environment}-asg"
      Environment = var.environment
      Purpose     = "auto-scaling-group"
      Compliance  = "financial-grade"
    })
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

  lifecycle {
    create_before_destroy = true
    ignore_changes       = [desired_capacity]
  }
}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "${var.app_name}-${var.environment}-scale-up"
  scaling_adjustment     = var.scale_up_adjustment
  adjustment_type        = "ChangeInCapacity"
  cooldown              = var.scale_up_cooldown
  autoscaling_group_name = aws_autoscaling_group.main.name
  policy_type           = "SimpleScaling"
}

resource "aws_autoscaling_policy" "scale_down" {
  name                   = "${var.app_name}-${var.environment}-scale-down"
  scaling_adjustment     = var.scale_down_adjustment
  adjustment_type        = "ChangeInCapacity"
  cooldown              = var.scale_down_cooldown
  autoscaling_group_name = aws_autoscaling_group.main.name
  policy_type           = "SimpleScaling"
}

# Target Tracking Scaling Policy for CPU
resource "aws_autoscaling_policy" "target_tracking_cpu" {
  name                   = "${var.app_name}-${var.environment}-target-tracking-cpu"
  autoscaling_group_name = aws_autoscaling_group.main.name
  policy_type           = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = var.target_cpu_utilization
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.app_name}-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = var.high_cpu_threshold
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.main.name
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-high-cpu-alarm"
    Environment = var.environment
    Purpose     = "auto-scaling-alarm"
    Compliance  = "financial-grade"
  })
}

resource "aws_cloudwatch_metric_alarm" "low_cpu" {
  alarm_name          = "${var.app_name}-${var.environment}-low-cpu"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = var.low_cpu_threshold
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = [aws_autoscaling_policy.scale_down.arn]

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.main.name
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-low-cpu-alarm"
    Environment = var.environment
    Purpose     = "auto-scaling-alarm"
    Compliance  = "financial-grade"
  })
}

# IAM Role for EC2 instances
resource "aws_iam_role" "main" {
  name = "${var.app_name}-${var.environment}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-ec2-role"
    Environment = var.environment
    Purpose     = "compute-role"
    Compliance  = "financial-grade"
  })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "main" {
  name = "${var.app_name}-${var.environment}-ec2-profile"
  role = aws_iam_role.main.name

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-ec2-profile"
    Environment = var.environment
    Purpose     = "compute-profile"
    Compliance  = "financial-grade"
  })
}

# IAM Policy for EC2 instances
resource "aws_iam_role_policy" "main" {
  name = "${var.app_name}-${var.environment}-ec2-policy"
  role = aws_iam_role.main.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData",
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "logs:PutLogEvents",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogStreams"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${var.ssm_parameter_path}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = var.secrets_manager_arns
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${var.app_data_bucket_arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = var.app_data_bucket_arn
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = var.kms_key_arn
      }
    ]
  })
}

# Attach AWS managed policies
resource "aws_iam_role_policy_attachment" "ssm_managed_instance_core" {
  role       = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "cloudwatch_agent_server_policy" {
  role       = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.app_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets           = var.public_subnet_ids

  enable_deletion_protection = var.environment == "prod"
  enable_http2              = true
  enable_waf_fail_open      = false

  # Access logs
  access_logs {
    bucket  = var.access_logs_bucket
    prefix  = "${var.app_name}-${var.environment}-alb"
    enabled = true
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-alb"
    Environment = var.environment
    Purpose     = "load-balancer"
    Compliance  = "financial-grade"
  })
}

# ALB Target Group
resource "aws_lb_target_group" "main" {
  name     = "${var.app_name}-${var.environment}-tg"
  port     = var.app_port
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  # Stickiness for session management
  stickiness {
    type            = "lb_cookie"
    cookie_duration = 86400
    enabled         = var.enable_stickiness
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-tg"
    Environment = var.environment
    Purpose     = "target-group"
    Compliance  = "financial-grade"
  })
}

# ALB Listener (HTTPS)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.ssl_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-https-listener"
    Environment = var.environment
    Purpose     = "https-listener"
    Compliance  = "financial-grade"
  })
}

# ALB Listener (HTTP to HTTPS redirect)
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-http-redirect"
    Environment = var.environment
    Purpose     = "http-redirect"
    Compliance  = "financial-grade"
  })
}

# WAF Association
resource "aws_wafv2_web_acl_association" "main" {
  count        = var.waf_web_acl_arn != "" ? 1 : 0
  resource_arn = aws_lb.main.arn
  web_acl_arn  = var.waf_web_acl_arn
}

# CloudWatch Log Group for application logs
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/ec2/${var.app_name}-${var.environment}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_id

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-app-logs"
    Environment = var.environment
    Purpose     = "application-logs"
    Compliance  = "financial-grade"
  })
}

# Systems Manager Parameter for application configuration
resource "aws_ssm_parameter" "app_config" {
  for_each = var.app_parameters

  name  = "${var.ssm_parameter_path}/${each.key}"
  type  = each.value.type
  value = each.value.value
  description = each.value.description

  tags = merge(var.common_tags, {
    Name        = "${var.app_name}-${var.environment}-${each.key}"
    Environment = var.environment
    Purpose     = "application-config"
    Compliance  = "financial-grade"
  })
}

# Scheduled Actions for cost optimization
resource "aws_autoscaling_schedule" "scale_down_evening" {
  count                  = var.enable_scheduled_scaling && var.environment != "prod" ? 1 : 0
  scheduled_action_name  = "${var.app_name}-${var.environment}-scale-down-evening"
  min_size              = 0
  max_size              = var.max_size
  desired_capacity      = 0
  recurrence            = "0 20 * * MON-FRI"  # 8 PM weekdays
  autoscaling_group_name = aws_autoscaling_group.main.name
}

resource "aws_autoscaling_schedule" "scale_up_morning" {
  count                  = var.enable_scheduled_scaling && var.environment != "prod" ? 1 : 0
  scheduled_action_name  = "${var.app_name}-${var.environment}-scale-up-morning"
  min_size              = var.min_size
  max_size              = var.max_size
  desired_capacity      = var.desired_capacity
  recurrence            = "0 8 * * MON-FRI"   # 8 AM weekdays
  autoscaling_group_name = aws_autoscaling_group.main.name
}

