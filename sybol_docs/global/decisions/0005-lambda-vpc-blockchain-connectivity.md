# ADR-0005: Deploy Lambda Function Inside VPC for Blockchain Node Connectivity

**Date:** 2026-03-17  
**Status:** Implemented

## Context

The `createAlastriaIdentity` Lambda function interacts with an Alastria redT blockchain node hosted on an EC2 instance (`i-0c9226bdc40f7dd9c`) within AWS `eu-west-1`.

The RPC endpoint of the node operates on port `22000`. The EC2 instance is protected by the security group `AlastriaNodeAccess` (`sg-098226edfce81ccd3`), which restricts inbound access to port `22000` to a specific set of trusted IP addresses.

By default, AWS Lambda functions run outside any VPC, using a shared AWS-managed network with dynamic, unpredictable egress IPs. This makes it impossible to whitelist Lambda as a trusted source in the security group without opening the port to the entire internet or managing a large and volatile CIDR range.

Connectivity tests confirmed that port `22000` on the blockchain node is silently filtered (no TCP RST, request times out) from any non-whitelisted IP, including the Lambda execution environment.

## Decision

Deploy the `createAlastriaIdentity` Lambda function inside the same AWS VPC as the blockchain EC2 node, using a dedicated security group for Lambda (`lambda-alastria-sg`). The `AlastriaNodeAccess` security group on the EC2 node will be updated to allow inbound TCP traffic on port `22000` from the Lambda security group, using security group referencing (not CIDR-based rules).

The Lambda will be attached to private subnets within the VPC. To retain access to AWS services (Secrets Manager), a VPC Endpoint or NAT Gateway must be present in the VPC.

## Decision Drivers

- Security: access to the blockchain node RPC port must remain restricted
- Reliability: Lambda must reliably reach the node without depending on external network paths
- Operational simplicity: security group referencing avoids managing IP whitelists
- AWS best practices: VPC placement is the recommended approach for Lambda-to-EC2 communication within the same account and region

## Considered Options

- **Option A — Open port 22000 to all Lambda egress IPs:** Not viable. Lambda does not have fixed egress IPs without a NAT Gateway. The Lambda IP range covers thousands of AWS addresses, effectively opening the port to the internet.

- **Option B — Assign a NAT Gateway with Elastic IP and whitelist it:** Viable but adds cost and operational complexity. A NAT Gateway must be provisioned and maintained; Elastic IP must be registered in the security group. Any infrastructure change could break connectivity silently.

- **Option C — Deploy Lambda in the same VPC (selected):** Lambda is attached to private subnets in the same VPC as the EC2 node. Access is granted via security group referencing, which is dynamic (no IP management), secure, and idiomatic for AWS-internal communication.

## Decision Outcome

Option C was selected because it provides the most secure and maintainable solution. Security group referencing eliminates the need to manage IP ranges and aligns with standard AWS network security practices for intra-VPC service communication.

## Consequences

### Positive

- Lambda can reliably connect to the blockchain node on port `22000` via private VPC networking
- Access is controlled by security group rules, not IP whitelists — no operational drift
- No public internet exposure of the RPC port
- Follows AWS Well-Architected Framework networking principles

### Negative

- Lambda inside a VPC has no default internet access; access to AWS Secrets Manager requires either a VPC Endpoint (`com.amazonaws.eu-west-1.secretsmanager`) or a NAT Gateway
- Lambda cold start time may increase slightly due to VPC ENI attachment
- Additional IAM permission `AWSLambdaVPCAccessExecutionRole` is required on the Lambda execution role

## Implementation Notes

1. Identify the VPC and private subnets of instance `i-0c9226bdc40f7dd9c`
2. Create a new security group `lambda-alastria-sg` in that VPC with no inbound rules and full outbound
3. Add an inbound rule to `AlastriaNodeAccess` (`sg-098226edfce81ccd3`) allowing TCP port `22000` from `lambda-alastria-sg` (SG-to-SG reference)
4. Attach policy `AWSLambdaVPCAccessExecutionRole` to the Lambda IAM role `createAlastriaIdentity-role`
5. Update Lambda configuration with `--vpc-config SubnetIds=...,SecurityGroupIds=lambda-alastria-sg`
6. Ensure a VPC Endpoint for Secrets Manager exists in the VPC, or route traffic through a NAT Gateway for AWS API access
