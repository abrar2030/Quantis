provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "model_artifacts" {
  bucket = "deepinsight-models-${var.environment}"
  acl    = "private"
}

resource "aws_sagemaker_model" "prod" {
  name               = "deepinsight-model"
  execution_role_arn = aws_iam_role.sagemaker.arn

  primary_container {
    image = "${aws_ecr_repository.model.repository_url}:latest"
  }
}
