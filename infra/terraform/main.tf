# One NVMe instance for a Base full node + searcher. Region is a variable on purpose: Base does not publish its
# sequencer location; choose by measured latency (infra/probe-latency.sh). Not applied from this repository.
terraform {
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}
variable "region" { default = "us-east-1" }
variable "instance_type" { default = "i7ie.3xlarge" } # 12 vCPU, 96 GiB, 7.5 TB NVMe; docs.base.org minimum is 8 cores / 64 GB / 2 TB NVMe
variable "ssh_cidr" { description = "your IP/32" }
provider "aws" { region = var.region }
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter { name = "name"; values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"] }
}
resource "aws_security_group" "node" {
  name = "base-node"
  ingress { from_port = 22; to_port = 22; protocol = "tcp"; cidr_blocks = [var.ssh_cidr] }
  ingress { from_port = 9222; to_port = 9222; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] } # p2p
  ingress { from_port = 9222; to_port = 9222; protocol = "udp"; cidr_blocks = ["0.0.0.0/0"] }
  egress  { from_port = 0; to_port = 0; protocol = "-1"; cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_instance" "node" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  vpc_security_group_ids      = [aws_security_group.node.id]
  associate_public_ip_address = true
  user_data                   = <<-EOT
    #!/bin/bash
    set -e
    apt-get update && apt-get install -y docker.io docker-compose-v2 mdadm
    mkfs.ext4 -F /dev/nvme1n1 && mkdir -p /data && mount /dev/nvme1n1 /data
    echo '/dev/nvme1n1 /data ext4 defaults,noatime 0 0' >> /etc/fstab
  EOT
  tags = { Name = "base-node-searcher" }
}
output "public_ip" { value = aws_instance.node.public_ip }
