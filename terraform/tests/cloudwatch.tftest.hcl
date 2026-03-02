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

run "lambda_log_group_name" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.lambda.name == "/aws/lambda/pdf-amplify-dev-s3-pipeline"
    error_message = "Lambda log group name should follow convention: /aws/lambda/{name_prefix}-s3-pipeline"
  }
}

run "lambda_log_group_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.lambda.retention_in_days == 14
    error_message = "Lambda log group retention should be 14 days"
  }
}

run "ecs_log_group_name" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.ecs.name == "/ecs/pdf-amplify-dev-embedding-pipeline"
    error_message = "ECS log group name should follow convention: /ecs/{name_prefix}-embedding-pipeline"
  }
}

run "ecs_log_group_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.ecs.retention_in_days == 14
    error_message = "ECS log group retention should be 14 days"
  }
}

run "api_gateway_log_group_name" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.api_gateway.name == "/aws/apigateway/pdf-amplify-dev-api"
    error_message = "API Gateway log group name should follow convention: /aws/apigateway/{name_prefix}-api"
  }
}

run "api_gateway_log_group_retention" {
  command = plan

  assert {
    condition     = aws_cloudwatch_log_group.api_gateway.retention_in_days == 7
    error_message = "API Gateway log group retention should be 7 days"
  }
}
