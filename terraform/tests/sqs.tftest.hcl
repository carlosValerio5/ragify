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

run "sqs_main_queue_name" {
  command = plan

  assert {
    condition     = aws_sqs_queue.main.name == "pdf-amplify-dev-queue"
    error_message = "Main SQS queue name should follow naming convention"
  }
}

run "sqs_dlq_name" {
  command = plan

  assert {
    condition     = aws_sqs_queue.dlq.name == "pdf-amplify-dev-dlq"
    error_message = "DLQ name should follow naming convention"
  }
}

run "sqs_main_queue_visibility_timeout" {
  command = plan

  assert {
    condition     = aws_sqs_queue.main.visibility_timeout_seconds == 300
    error_message = "Main queue visibility timeout should be 300 seconds (5 min)"
  }
}

run "sqs_main_queue_retention" {
  command = plan

  assert {
    condition     = aws_sqs_queue.main.message_retention_seconds == 86400
    error_message = "Main queue message retention should be 86400 seconds (1 day)"
  }
}

run "sqs_main_queue_long_polling" {
  command = plan

  assert {
    condition     = aws_sqs_queue.main.receive_wait_time_seconds == 20
    error_message = "Main queue should use long polling with 20 second wait"
  }
}

run "sqs_dlq_retention" {
  command = plan

  assert {
    condition     = aws_sqs_queue.dlq.message_retention_seconds == 1209600
    error_message = "DLQ message retention should be 1209600 seconds (14 days)"
  }
}
