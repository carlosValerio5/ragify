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

run "lambda_exec_role_name" {
  command = plan

  assert {
    condition     = aws_iam_role.lambda_exec.name == "pdf-amplify-dev-lambda-exec"
    error_message = "Lambda execution role name should follow naming convention"
  }
}

run "ecs_execution_role_name" {
  command = plan

  assert {
    condition     = aws_iam_role.ecs_execution.name == "pdf-amplify-dev-ecs-execution"
    error_message = "ECS execution role name should follow naming convention"
  }
}

run "ecs_task_role_name" {
  command = plan

  assert {
    condition     = aws_iam_role.ecs_task.name == "pdf-amplify-dev-ecs-task"
    error_message = "ECS task role name should follow naming convention"
  }
}

run "lambda_policy_name" {
  command = plan

  assert {
    condition     = aws_iam_role_policy.lambda_permissions.name == "pdf-amplify-dev-lambda-permissions"
    error_message = "Lambda permissions policy name should follow naming convention"
  }
}

run "ecs_execution_extra_policy_name" {
  command = plan

  assert {
    condition     = aws_iam_role_policy.ecs_execution_extra.name == "pdf-amplify-dev-ecs-execution-extra"
    error_message = "ECS execution extra policy name should follow naming convention"
  }
}

run "ecs_task_permissions_policy_name" {
  command = plan

  assert {
    condition     = aws_iam_role_policy.ecs_task_permissions.name == "pdf-amplify-dev-ecs-task-permissions"
    error_message = "ECS task permissions policy name should follow naming convention"
  }
}
