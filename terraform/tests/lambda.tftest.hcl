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

run "lambda_function_name" {
  command = plan

  assert {
    condition     = aws_lambda_function.s3_pipeline.function_name == "pdf-amplify-dev-s3-pipeline"
    error_message = "Lambda function name should follow naming convention: {project}-{env}-s3-pipeline"
  }
}

run "lambda_runtime" {
  command = plan

  assert {
    condition     = aws_lambda_function.s3_pipeline.runtime == "python3.13"
    error_message = "Lambda runtime should be python3.13"
  }
}

run "lambda_timeout" {
  command = plan

  assert {
    condition     = aws_lambda_function.s3_pipeline.timeout == 30
    error_message = "Lambda timeout should be 30 seconds"
  }
}

run "lambda_memory" {
  command = plan

  assert {
    condition     = aws_lambda_function.s3_pipeline.memory_size == 256
    error_message = "Lambda memory should be 256 MB"
  }
}

run "lambda_handler" {
  command = plan

  assert {
    condition     = aws_lambda_function.s3_pipeline.handler == "app.main.handler"
    error_message = "Lambda handler should be app.main.handler"
  }
}

run "lambda_environment_variables" {
  command = plan

  assert {
    condition     = aws_lambda_function.s3_pipeline.environment[0].variables["S3_BUCKET_NAME"] == "pdf-amplify-system"
    error_message = "Lambda S3_BUCKET_NAME env var should match bucket name"
  }

  assert {
    condition     = aws_lambda_function.s3_pipeline.environment[0].variables["S3_REGION"] == "us-east-1"
    error_message = "Lambda S3_REGION env var should match aws_region"
  }

  assert {
    condition     = aws_lambda_function.s3_pipeline.environment[0].variables["SECRET_REGION"] == "us-east-1"
    error_message = "Lambda SECRET_REGION env var should match aws_region"
  }
}

run "api_gateway_protocol" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_api.http_api.protocol_type == "HTTP"
    error_message = "API Gateway protocol should be HTTP"
  }
}

run "api_gateway_name" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_api.http_api.name == "pdf-amplify-dev-api"
    error_message = "API Gateway name should follow naming convention"
  }
}

run "api_gateway_upload_route" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_route.upload_route.route_key == "POST /documents/upload"
    error_message = "Upload route key should be POST /documents/upload"
  }
}

run "api_gateway_health_route" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_route.health_route.route_key == "GET /health"
    error_message = "Health route key should be GET /health"
  }
}

run "api_gateway_catch_all_route" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_route.catch_all.route_key == "$default"
    error_message = "Catch-all route key should be $default"
  }
}

run "api_gateway_stage_auto_deploy" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_stage.lambda_stage.auto_deploy == true
    error_message = "API Gateway stage should have auto_deploy enabled"
  }
}

run "api_gateway_stage_name" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_stage.lambda_stage.name == "dev"
    error_message = "API Gateway stage name should match environment"
  }
}

run "lambda_integration_type" {
  command = plan

  assert {
    condition     = aws_apigatewayv2_integration.lambda_integration.integration_type == "AWS_PROXY"
    error_message = "Lambda integration type should be AWS_PROXY"
  }

  assert {
    condition     = aws_apigatewayv2_integration.lambda_integration.payload_format_version == "2.0"
    error_message = "Payload format version should be 2.0"
  }
}
