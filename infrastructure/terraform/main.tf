# Quantis Infrastructure - Simplified Main Configuration
# This is a simplified version for validation purposes

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = var.default_tags
  }
}

# Random ID for unique naming
resource "random_id" "suffix" {
  byte_length = 4
}

# S3 bucket for application data (fixed deprecated ACL)
resource "aws_s3_bucket" "app_data" {
  bucket = "${var.app_name}-${var.environment}-data-${random_id.suffix.hex}"
  
  tags = merge(var.default_tags, {
    Name        = "${var.app_name}-${var.environment}-data"
    Environment = var.environment
    Purpose     = "application-data"
  })
}

# S3 bucket ACL (separate resource as per AWS provider v4+)
resource "aws_s3_bucket_acl" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  acl    = "private"
}

# S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "app_data" {
  bucket = aws_s3_bucket.app_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "app_data" {
  bucket = aws_s3_bucket.app_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ECR Repository for model images
resource "aws_ecr_repository" "model" {
  name                 = "${var.app_name}-${var.environment}-model"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(var.default_tags, {
    Name        = "${var.app_name}-${var.environment}-model"
    Environment = var.environment
    Purpose     = "container-registry"
  })
}

# IAM Role for SageMaker
resource "aws_iam_role" "sagemaker" {
  name = "${var.app_name}-${var.environment}-sagemaker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.default_tags, {
    Name        = "${var.app_name}-${var.environment}-sagemaker-role"
    Environment = var.environment
    Purpose     = "machine-learning"
  })
}

# IAM Policy for SageMaker
resource "aws_iam_role_policy" "sagemaker" {
  name = "${var.app_name}-${var.environment}-sagemaker-policy"
  role = aws_iam_role.sagemaker.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.app_data.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.app_data.arn
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# SageMaker Model
resource "aws_sagemaker_model" "main" {
  name               = "${var.app_name}-${var.environment}-model"
  execution_role_arn = aws_iam_role.sagemaker.arn

  primary_container {
    image = "${aws_ecr_repository.model.repository_url}:latest"
  }

  tags = merge(var.default_tags, {
    Name        = "${var.app_name}-${var.environment}-model"
    Environment = var.environment
    Purpose     = "machine-learning-model"
  })
}
