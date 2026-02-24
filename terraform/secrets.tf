resource "aws_secretsmanager_secret" "app_credentials" {
  name                    = "${local.name_prefix}-credentials"
  description             = "Credentials for the PDF Amplify RAG system"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "app_credentials" {
  secret_id = aws_secretsmanager_secret.app_credentials.id

  # change values for vars with aws cli
  secret_string = jsonencode({
    aws_access_key_id     = "CHANGE_ME"
    aws_secret_access_key = "CHANGE_ME"
    s3_bucket_name        = var.s3_bucket_name
    s3_region             = var.aws_region
    sqs_queue_url         = aws_sqs_queue.main.url
    sqs_dlq_url           = aws_sqs_queue.dlq.url
    pinecone_api_key      = "CHANGE_ME"
    pinecone_index_name   = "CHANGE_ME"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
