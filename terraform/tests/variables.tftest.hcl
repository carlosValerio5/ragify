mock_provider "aws" {}

override_data {
  target = data.aws_iam_policy_document.lambda_assume_role
  values = {
    json = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  }
}

override_data {
  target = data.aws_iam_policy_document.ecs_assume_role
  values = {
    json = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs-tasks.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  }
}

override_data {
  target = data.aws_iam_policy_document.lambda_permissions
  values = {
    json = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"logs:CreateLogStream\"],\"Resource\":[\"*\"]}]}"
  }
}

override_data {
  target = data.aws_iam_policy_document.ecs_execution_extra
  values = {
    json = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"secretsmanager:GetSecretValue\"],\"Resource\":[\"*\"]}]}"
  }
}

override_data {
  target = data.aws_iam_policy_document.ecs_task_permissions
  values = {
    json = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"sqs:ReceiveMessage\"],\"Resource\":[\"*\"]}]}"
  }
}

run "default_aws_region" {
  command = plan

  assert {
    condition     = var.aws_region == "us-east-1"
    error_message = "Default AWS region should be us-east-1"
  }
}

run "default_project_name" {
  command = plan

  assert {
    condition     = var.project_name == "pdf-amplify"
    error_message = "Default project name should be pdf-amplify"
  }
}

run "default_environment" {
  command = plan

  assert {
    condition     = var.environment == "dev"
    error_message = "Default environment should be dev"
  }
}

run "default_s3_bucket_name" {
  command = plan

  assert {
    condition     = var.s3_bucket_name == "pdf-amplify-system"
    error_message = "Default S3 bucket name should be pdf-amplify-system"
  }
}

run "default_ecs_cpu" {
  command = plan

  assert {
    condition     = var.ecs_cpu == 512
    error_message = "Default ECS CPU should be 512"
  }
}

run "default_ecs_memory" {
  command = plan

  assert {
    condition     = var.ecs_memory == 1024
    error_message = "Default ECS memory should be 1024"
  }
}

run "default_ecs_desired_count" {
  command = plan

  assert {
    condition     = var.ecs_desired_count == 1
    error_message = "Default ECS desired count should be 1"
  }
}

run "default_vpc_cidr" {
  command = plan

  assert {
    condition     = var.vpc_cidr == "10.0.0.0/16"
    error_message = "Default VPC CIDR should be 10.0.0.0/16"
  }
}

run "default_public_subnet_cidrs" {
  command = plan

  assert {
    condition     = length(var.public_subnet_cidrs) == 2
    error_message = "Should have 2 public subnet CIDRs by default"
  }

  assert {
    condition     = var.public_subnet_cidrs[0] == "10.0.1.0/24"
    error_message = "First public subnet CIDR should be 10.0.1.0/24"
  }

  assert {
    condition     = var.public_subnet_cidrs[1] == "10.0.2.0/24"
    error_message = "Second public subnet CIDR should be 10.0.2.0/24"
  }
}

run "default_availability_zones" {
  command = plan

  assert {
    condition     = length(var.availability_zones) == 2
    error_message = "Should have 2 availability zones by default"
  }

  assert {
    condition     = var.availability_zones[0] == "us-east-1a"
    error_message = "First AZ should be us-east-1a"
  }

  assert {
    condition     = var.availability_zones[1] == "us-east-1b"
    error_message = "Second AZ should be us-east-1b"
  }
}

run "custom_environment_override" {
  command = plan

  variables {
    environment = "prod"
  }

  assert {
    condition     = var.environment == "prod"
    error_message = "Environment should accept custom override"
  }
}
