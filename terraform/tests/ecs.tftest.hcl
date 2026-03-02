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

run "ecs_cluster_name" {
  command = plan

  assert {
    condition     = aws_ecs_cluster.main.name == "pdf-amplify-dev-cluster"
    error_message = "ECS cluster name should follow naming convention"
  }
}

run "ecs_cluster_container_insights" {
  command = plan

  assert {
    condition     = length([for s in aws_ecs_cluster.main.setting : s if s.name == "containerInsights" && s.value == "enabled"]) == 1
    error_message = "ECS cluster should have containerInsights enabled"
  }
}

run "ecs_task_definition_family" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.embedding_pipeline.family == "pdf-amplify-dev-embedding-pipeline"
    error_message = "Task definition family should follow naming convention"
  }
}

run "ecs_task_definition_fargate" {
  command = plan

  assert {
    condition     = contains(aws_ecs_task_definition.embedding_pipeline.requires_compatibilities, "FARGATE")
    error_message = "Task definition should require FARGATE compatibility"
  }
}

run "ecs_task_definition_network_mode" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.embedding_pipeline.network_mode == "awsvpc"
    error_message = "Task definition network mode should be awsvpc"
  }
}

run "ecs_task_definition_cpu_memory" {
  command = plan

  assert {
    condition     = aws_ecs_task_definition.embedding_pipeline.cpu == "512"
    error_message = "Task definition CPU should match ecs_cpu variable default (512)"
  }

  assert {
    condition     = aws_ecs_task_definition.embedding_pipeline.memory == "1024"
    error_message = "Task definition memory should match ecs_memory variable default (1024)"
  }
}

run "ecs_service_name" {
  command = plan

  assert {
    condition     = aws_ecs_service.embedding_pipeline.name == "pdf-amplify-dev-embedding"
    error_message = "ECS service name should follow naming convention"
  }
}

run "ecs_service_desired_count" {
  command = plan

  assert {
    condition     = aws_ecs_service.embedding_pipeline.desired_count == 1
    error_message = "ECS service desired count should match variable default (1)"
  }
}

run "ecs_service_launch_type" {
  command = plan

  assert {
    condition     = aws_ecs_service.embedding_pipeline.launch_type == "FARGATE"
    error_message = "ECS service launch type should be FARGATE"
  }
}

run "ecs_service_public_ip" {
  command = plan

  assert {
    condition     = aws_ecs_service.embedding_pipeline.network_configuration[0].assign_public_ip == true
    error_message = "ECS service should assign public IP"
  }
}

run "ecs_custom_cpu_memory_override" {
  command = plan

  variables {
    ecs_cpu    = 1024
    ecs_memory = 2048
  }

  assert {
    condition     = aws_ecs_task_definition.embedding_pipeline.cpu == "1024"
    error_message = "Task definition CPU should accept custom override"
  }

  assert {
    condition     = aws_ecs_task_definition.embedding_pipeline.memory == "2048"
    error_message = "Task definition memory should accept custom override"
  }
}
