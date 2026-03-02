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

run "s3_bucket_name" {
  command = plan

  assert {
    condition     = aws_s3_bucket.bucket.bucket == "pdf-amplify-system"
    error_message = "S3 bucket name should match the s3_bucket_name variable default"
  }
}

run "s3_versioning_enabled" {
  command = plan

  assert {
    condition     = aws_s3_bucket_versioning.bucket_versioning.versioning_configuration[0].status == "Enabled"
    error_message = "S3 bucket versioning should be enabled"
  }
}

run "s3_sse_algorithm" {
  command = plan

  assert {
    condition     = length([for r in aws_s3_bucket_server_side_encryption_configuration.bucket_sse.rule : r if one(r.apply_server_side_encryption_by_default[*].sse_algorithm) == "AES256"]) == 1
    error_message = "S3 bucket SSE should use AES256"
  }
}

run "s3_public_access_block" {
  command = plan

  assert {
    condition     = aws_s3_bucket_public_access_block.bucket_public_access.block_public_acls == true
    error_message = "block_public_acls should be true"
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.bucket_public_access.block_public_policy == true
    error_message = "block_public_policy should be true"
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.bucket_public_access.ignore_public_acls == true
    error_message = "ignore_public_acls should be true"
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.bucket_public_access.restrict_public_buckets == true
    error_message = "restrict_public_buckets should be true"
  }
}

run "s3_notification_filter_suffix" {
  command = plan

  assert {
    condition     = aws_s3_bucket_notification.pdf_upload_notification.queue[0].filter_suffix == ".pdf"
    error_message = "S3 notification should filter for .pdf suffix"
  }

  assert {
    condition     = contains(aws_s3_bucket_notification.pdf_upload_notification.queue[0].events, "s3:ObjectCreated:*")
    error_message = "S3 notification should trigger on ObjectCreated events"
  }
}
