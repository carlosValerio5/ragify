resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "embedding_pipeline" {
  family                   = "${local.name_prefix}-embedding-pipeline"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "embedding-pipeline"
      image     = "${aws_ecr_repository.embedding_pipeline.repository_url}:${var.embedding_image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "SECRET_NAME", value = aws_secretsmanager_secret.app_credentials.name },
        { name = "SECRET_REGION", value = var.aws_region },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "SQS_QUEUE_URL", value = aws_sqs_queue.main.url },
        { name = "SQS_DLQ_URL", value = aws_sqs_queue.dlq.url },
        { name = "S3_BUCKET_NAME", value = var.s3_bucket_name },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "embedding"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/embedding/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

resource "aws_ecs_service" "embedding_pipeline" {
  name            = "${local.name_prefix}-embedding"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.embedding_pipeline.arn
  desired_count   = var.ecs_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  depends_on = [
    aws_iam_role_policy.ecs_task_permissions,
    aws_iam_role_policy.ecs_execution_extra,
  ]
}
