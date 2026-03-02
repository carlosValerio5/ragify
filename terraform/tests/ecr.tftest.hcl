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

run "ecr_repository_name" {
  command = plan

  assert {
    condition     = aws_ecr_repository.embedding_pipeline.name == "pdf-amplify-dev-embedding-pipeline"
    error_message = "ECR repository name should follow naming convention"
  }
}

run "ecr_image_tag_mutability" {
  command = plan

  assert {
    condition     = aws_ecr_repository.embedding_pipeline.image_tag_mutability == "MUTABLE"
    error_message = "ECR image tag mutability should be MUTABLE"
  }
}

run "ecr_force_delete" {
  command = plan

  assert {
    condition     = aws_ecr_repository.embedding_pipeline.force_delete == true
    error_message = "ECR force_delete should be true"
  }
}

run "ecr_scan_on_push" {
  command = plan

  assert {
    condition     = aws_ecr_repository.embedding_pipeline.image_scanning_configuration[0].scan_on_push == true
    error_message = "ECR scan_on_push should be enabled"
  }
}
