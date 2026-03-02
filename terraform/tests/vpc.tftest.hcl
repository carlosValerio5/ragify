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

run "vpc_cidr_block" {
  command = plan

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block should match vpc_cidr variable default"
  }
}

run "vpc_dns_support" {
  command = plan

  assert {
    condition     = aws_vpc.main.enable_dns_support == true
    error_message = "VPC DNS support should be enabled"
  }

  assert {
    condition     = aws_vpc.main.enable_dns_hostnames == true
    error_message = "VPC DNS hostnames should be enabled"
  }
}

run "vpc_name_tag" {
  command = plan

  assert {
    condition     = aws_vpc.main.tags["Name"] == "pdf-amplify-dev-vpc"
    error_message = "VPC Name tag should follow naming convention"
  }
}

run "public_subnet_count" {
  command = plan

  assert {
    condition     = length(aws_subnet.public) == 2
    error_message = "Should create 2 public subnets"
  }
}

run "public_subnet_cidrs" {
  command = plan

  assert {
    condition     = aws_subnet.public[0].cidr_block == "10.0.1.0/24"
    error_message = "First public subnet CIDR should be 10.0.1.0/24"
  }

  assert {
    condition     = aws_subnet.public[1].cidr_block == "10.0.2.0/24"
    error_message = "Second public subnet CIDR should be 10.0.2.0/24"
  }
}

run "public_subnet_auto_assign_ip" {
  command = plan

  assert {
    condition     = aws_subnet.public[0].map_public_ip_on_launch == true
    error_message = "Public subnets should auto-assign public IPs"
  }

  assert {
    condition     = aws_subnet.public[1].map_public_ip_on_launch == true
    error_message = "Public subnets should auto-assign public IPs"
  }
}

run "internet_gateway_name_tag" {
  command = plan

  assert {
    condition     = aws_internet_gateway.main.tags["Name"] == "pdf-amplify-dev-igw"
    error_message = "Internet gateway Name tag should follow naming convention"
  }
}

run "route_table_default_route" {
  command = plan

  assert {
    condition     = length([for r in aws_route_table.public.route : r if r.cidr_block == "0.0.0.0/0"]) == 1
    error_message = "Public route table should have a default route (0.0.0.0/0)"
  }
}

run "route_table_association_count" {
  command = plan

  assert {
    condition     = length(aws_route_table_association.public) == 2
    error_message = "Should have 2 route table associations (one per subnet)"
  }
}

run "security_group_name" {
  command = plan

  assert {
    condition     = aws_security_group.ecs_tasks.name == "pdf-amplify-dev-ecs-tasks-sg"
    error_message = "Security group name should follow naming convention"
  }
}

run "security_group_egress" {
  command = plan

  assert {
    condition = length([
      for e in aws_security_group.ecs_tasks.egress : e
      if e.from_port == 0 && e.to_port == 0 && e.protocol == "-1" && contains(e.cidr_blocks, "0.0.0.0/0")
    ]) == 1
    error_message = "Security group should have an egress rule allowing all traffic to 0.0.0.0/0"
  }
}
