# Backup and Recovery

## Purpose

This document defines backup strategies, recovery procedures, and disaster recovery protocols for the Sybol multi-tenant platform.

## Context

Data protection is critical for maintaining service reliability and meeting compliance requirements. The platform implements automated backups, point-in-time recovery, and cross-region replication to ensure data durability and availability.

---

## Recovery Objectives

| Metric | Target | Description |
|--------|--------|-------------|
| RPO (Recovery Point Objective) | 5 minutes | Maximum acceptable data loss |
| RTO (Recovery Time Objective) | 1 hour | Maximum acceptable downtime |
| Backup Frequency | Continuous + Daily snapshots | RDS automated backups + manual snapshots |
| Backup Retention | 7 days automated, 30 days manual | Compliance requirement |

---

## RDS Database Backups

### Automated Backups

RDS Aurora automatically backs up the database cluster continuously.

#### Verify Automated Backup Configuration

```bash
# Check backup settings
aws rds describe-db-clusters \
  --db-cluster-identifier sybol-cluster \
  --query 'DBClusters[0].[BackupRetentionPeriod,PreferredBackupWindow]'
```

Expected output:
```
[
    7,
    "03:00-04:00"
]
```

#### Modify Backup Retention

```bash
# Extend backup retention to 14 days
aws rds modify-db-cluster \
  --db-cluster-identifier sybol-cluster \
  --backup-retention-period 14 \
  --preferred-backup-window "03:00-04:00" \
  --apply-immediately
```

#### Configure Backup Window

Set backup window during low-traffic periods:

```bash
aws rds modify-db-cluster \
  --db-cluster-identifier sybol-cluster \
  --preferred-backup-window "02:00-03:00" \
  --apply-immediately
```

### Manual Snapshots

Create manual snapshots before major changes or for long-term retention.

#### Create Manual Snapshot

```bash
# Create snapshot with descriptive name
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier sybol-cluster \
  --db-cluster-snapshot-identifier sybol-cluster-before-migration-2024-03-10
```

#### List Snapshots

```bash
# List all manual snapshots
aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier sybol-cluster \
  --snapshot-type manual \
  --query 'DBClusterSnapshots[*].[DBClusterSnapshotIdentifier,SnapshotCreateTime,Status]' \
  --output table
```

#### Delete Old Snapshots

```bash
# Delete snapshot (manual snapshots are not auto-deleted)
aws rds delete-db-cluster-snapshot \
  --db-cluster-snapshot-identifier sybol-cluster-before-migration-2024-03-10
```

### Point-in-Time Recovery (PITR)

Restore database to any point within the backup retention period.

#### List Available Restore Times

```bash
# Get earliest and latest restore time
aws rds describe-db-clusters \
  --db-cluster-identifier sybol-cluster \
  --query 'DBClusters[0].[EarliestRestorableTime,LatestRestorableTime]'
```

#### Restore to Point in Time

```bash
# Restore cluster to specific time
aws rds restore-db-cluster-to-point-in-time \
  --source-db-cluster-identifier sybol-cluster \
  --db-cluster-identifier sybol-cluster-restored \
  --restore-to-time "2024-03-10T14:30:00Z" \
  --vpc-security-group-ids sg-rds123 \
  --db-subnet-group-name default-sybol-vpc
```

⏱️ Restore typically takes 10-30 minutes depending on database size.

#### Verify Restored Cluster

```bash
# Check restoration status
aws rds describe-db-clusters \
  --db-cluster-identifier sybol-cluster-restored \
  --query 'DBClusters[0].Status'

# Connect and verify data
psql -h sybol-cluster-restored.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -d catalog \
     -c "SELECT COUNT(*) FROM catalog_entries;"
```

### Cross-Region Backup Replication

Enable cross-region replication for disaster recovery.

#### Create Read Replica in Another Region

```bash
# Create cross-region read replica
aws rds create-db-cluster \
  --db-cluster-identifier sybol-cluster-replica-us-east-1 \
  --replication-source-identifier arn:aws:rds:eu-west-1:ACCOUNT_ID:cluster:sybol-cluster \
  --engine aurora-postgresql \
  --region us-east-1
```

#### Promote Read Replica (Disaster Recovery)

```bash
# In case of regional failure, promote replica
aws rds promote-read-replica-db-cluster \
  --db-cluster-identifier sybol-cluster-replica-us-east-1 \
  --region us-east-1
```

---

## Individual Database Backups

### Export Tenant Database

For tenant-specific backups or migrations:

```bash
#!/bin/bash
# Script: backup-tenant-database.sh

TENANT_ID=$1
BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="backup_tenant_${TENANT_ID}_${BACKUP_DATE}.sql"

# Export database
pg_dump -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
  -U postgres \
  -d tenant_${TENANT_ID} \
  --format=custom \
  --compress=9 \
  --file=$BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://sybol-backups/databases/tenant_${TENANT_ID}/

# Clean up local file
rm $BACKUP_FILE

echo "Backup completed: s3://sybol-backups/databases/tenant_${TENANT_ID}/$BACKUP_FILE"
```

#### Restore from Backup

```bash
#!/bin/bash
# Script: restore-tenant-database.sh

TENANT_ID=$1
BACKUP_FILE=$2

# Download backup from S3
aws s3 cp s3://sybol-backups/databases/tenant_${TENANT_ID}/$BACKUP_FILE .

# Restore database
pg_restore -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
  -U postgres \
  -d tenant_${TENANT_ID} \
  --clean \
  --if-exists \
  $BACKUP_FILE

echo "Restore completed for tenant_${TENANT_ID}"
```

### Automated Daily Backups

Schedule daily backups using Lambda and EventBridge.

#### Lambda Function for Automated Backup

```python
# lambda_function.py
import boto3
import subprocess
import os
from datetime import datetime

s3 = boto3.client('s3')
rds = boto3.client('rds')

BACKUP_BUCKET = 'sybol-backups'
CLUSTER_ENDPOINT = os.environ['CLUSTER_ENDPOINT']

def lambda_handler(event, context):
    """Backup all tenant databases"""
    
    # Get list of tenant databases
    databases = get_tenant_databases()
    
    for db_name in databases:
        backup_database(db_name)
    
    return {
        'statusCode': 200,
        'body': f'Backed up {len(databases)} databases'
    }

def get_tenant_databases():
    """Query PostgreSQL for tenant databases"""
    import psycopg2
    
    conn = psycopg2.connect(
        host=CLUSTER_ENDPOINT,
        database='postgres',
        user='postgres',
        password=os.environ['DB_PASSWORD']
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT datname FROM pg_database WHERE datname LIKE 'tenant_%'")
    
    databases = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return databases

def backup_database(db_name):
    """Backup single database to S3"""
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_file = f'/tmp/{db_name}_{timestamp}.sql'
    
    # Run pg_dump
    subprocess.run([
        'pg_dump',
        '-h', CLUSTER_ENDPOINT,
        '-U', 'postgres',
        '-d', db_name,
        '--format=custom',
        '--compress=9',
        '--file', backup_file
    ], check=True)
    
    # Upload to S3
    s3_key = f'databases/{db_name}/{db_name}_{timestamp}.sql'
    s3.upload_file(backup_file, BACKUP_BUCKET, s3_key)
    
    # Clean up
    os.remove(backup_file)
    
    print(f'Backed up {db_name} to s3://{BACKUP_BUCKET}/{s3_key}')
```

#### EventBridge Rule for Daily Backup

```bash
# Create EventBridge rule for daily backup at 2 AM
aws events put-rule \
  --name daily-database-backup \
  --schedule-expression "cron(0 2 * * ? *)" \
  --state ENABLED

# Add Lambda as target
aws events put-targets \
  --rule daily-database-backup \
  --targets "Id"="1","Arn"="arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:database-backup"
```

---

## S3 Backup Strategy

### Frontend Static Files

#### Enable S3 Versioning

```bash
# Enable versioning on frontend buckets
for BUCKET in $(aws s3 ls | grep 'staging-wallet-frontend' | awk '{print $3}'); do
  aws s3api put-bucket-versioning \
    --bucket $BUCKET \
    --versioning-configuration Status=Enabled
  
  echo "Versioning enabled for $BUCKET"
done
```

#### Configure Lifecycle Policy

```bash
# Create lifecycle policy to expire old versions after 30 days
cat > lifecycle-policy.json <<EOF
{
  "Rules": [
    {
      "Id": "ExpireOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 30
      }
    },
    {
      "Id": "ExpireDeleteMarkers",
      "Status": "Enabled",
      "Expiration": {
        "ExpiredObjectDeleteMarker": true
      }
    }
  ]
}
EOF

# Apply lifecycle policy
for BUCKET in $(aws s3 ls | grep 'staging-wallet-frontend' | awk '{print $3}'); do
  aws s3api put-bucket-lifecycle-configuration \
    --bucket $BUCKET \
    --lifecycle-configuration file://lifecycle-policy.json
done
```

#### Restore Previous Version

```bash
# List versions of specific file
aws s3api list-object-versions \
  --bucket repsol-staging-wallet-frontend \
  --prefix index.html

# Restore specific version
aws s3api copy-object \
  --bucket repsol-staging-wallet-frontend \
  --copy-source "repsol-staging-wallet-frontend/index.html?versionId=VERSION_ID" \
  --key index.html
```

### Cross-Region Replication

Enable cross-region replication for critical buckets.

#### Create Replication Configuration

```bash
# Create replication role
aws iam create-role \
  --role-name S3ReplicationRole \
  --assume-role-policy-document file://s3-replication-trust-policy.json

# Attach replication policy
aws iam put-role-policy \
  --role-name S3ReplicationRole \
  --policy-name S3ReplicationPolicy \
  --policy-document file://s3-replication-policy.json

# Enable replication
aws s3api put-bucket-replication \
  --bucket repsol-staging-wallet-frontend \
  --replication-configuration file://replication-config.json
```

**replication-config.json:**

```json
{
  "Role": "arn:aws:iam::ACCOUNT_ID:role/S3ReplicationRole",
  "Rules": [
    {
      "Status": "Enabled",
      "Priority": 1,
      "DeleteMarkerReplication": {"Status": "Enabled"},
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::repsol-staging-wallet-frontend-replica",
        "ReplicationTime": {
          "Status": "Enabled",
          "Time": {"Minutes": 15}
        },
        "Metrics": {
          "Status": "Enabled",
          "EventThreshold": {"Minutes": 15}
        }
      }
    }
  ]
}
```

---

## Secrets Manager Backups

### Export Secrets

```bash
#!/bin/bash
# Script: backup-secrets.sh

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="secrets_backup_${BACKUP_DATE}.json"

# Get all secret names
SECRET_NAMES=$(aws secretsmanager list-secrets \
  --query 'SecretList[*].Name' \
  --output text)

# Export each secret
echo "{" > $BACKUP_FILE
first=true

for SECRET_NAME in $SECRET_NAMES; do
  if [ "$first" = true ]; then
    first=false
  else
    echo "," >> $BACKUP_FILE
  fi
  
  echo "  \"$SECRET_NAME\": " >> $BACKUP_FILE
  aws secretsmanager get-secret-value \
    --secret-id "$SECRET_NAME" \
    --query 'SecretString' \
    --output json >> $BACKUP_FILE
done

echo "}" >> $BACKUP_FILE

# Encrypt backup file
aws kms encrypt \
  --key-id alias/backup-encryption \
  --plaintext fileb://$BACKUP_FILE \
  --output text \
  --query CiphertextBlob | base64 --decode > ${BACKUP_FILE}.encrypted

# Upload to S3
aws s3 cp ${BACKUP_FILE}.encrypted s3://sybol-backups/secrets/

# Clean up
rm $BACKUP_FILE ${BACKUP_FILE}.encrypted

echo "Secrets backup completed: s3://sybol-backups/secrets/${BACKUP_FILE}.encrypted"
```

### Restore Secrets

```bash
#!/bin/bash
# Script: restore-secrets.sh

BACKUP_FILE=$1

# Download encrypted backup
aws s3 cp s3://sybol-backups/secrets/$BACKUP_FILE .

# Decrypt backup
aws kms decrypt \
  --ciphertext-blob fileb://$BACKUP_FILE \
  --output text \
  --query Plaintext | base64 --decode > secrets.json

# Restore each secret
jq -r 'to_entries[] | "\(.key)|\(.value)"' secrets.json | while IFS='|' read -r name value; do
  # Check if secret exists
  if aws secretsmanager describe-secret --secret-id "$name" 2>/dev/null; then
    # Update existing secret
    aws secretsmanager update-secret \
      --secret-id "$name" \
      --secret-string "$value"
  else
    # Create new secret
    aws secretsmanager create-secret \
      --name "$name" \
      --secret-string "$value"
  fi
  
  echo "Restored secret: $name"
done

# Clean up
rm $BACKUP_FILE secrets.json
```

---

## Configuration Backups

### Export Infrastructure Configuration

```bash
#!/bin/bash
# Script: backup-infrastructure-config.sh

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="infra_backup_${BACKUP_DATE}"

mkdir -p $BACKUP_DIR

# Export CloudFormation stacks
aws cloudformation list-stacks \
  --query 'StackSummaries[?StackStatus==`CREATE_COMPLETE` || StackStatus==`UPDATE_COMPLETE`].StackName' \
  --output text | while read STACK_NAME; do
  
  aws cloudformation get-template \
    --stack-name $STACK_NAME \
    --query 'TemplateBody' \
    > $BACKUP_DIR/${STACK_NAME}.json
done

# Export Lambda configurations
aws lambda list-functions --query 'Functions[*].FunctionName' --output text | while read FUNC_NAME; do
  aws lambda get-function-configuration \
    --function-name $FUNC_NAME \
    > $BACKUP_DIR/lambda_${FUNC_NAME}.json
done

# Export API Gateway configurations
aws apigatewayv2 get-apis --query 'Items[*].ApiId' --output text | while read API_ID; do
  aws apigatewayv2 export-api \
    --api-id $API_ID \
    --output-type JSON \
    --specification OAS30 \
    > $BACKUP_DIR/api_${API_ID}.json
done

# Compress and upload
tar -czf ${BACKUP_DIR}.tar.gz $BACKUP_DIR
aws s3 cp ${BACKUP_DIR}.tar.gz s3://sybol-backups/infrastructure/

# Clean up
rm -rf $BACKUP_DIR ${BACKUP_DIR}.tar.gz

echo "Infrastructure backup completed: s3://sybol-backups/infrastructure/${BACKUP_DIR}.tar.gz"
```

---

## Disaster Recovery Procedures

### Complete System Recovery

In case of catastrophic failure requiring full system recovery:

#### Phase 1: Infrastructure Recovery (2-4 hours)

```bash
# 1. Restore core infrastructure from CDK
cd infraestructure/CoreInfra
cdk deploy --all --require-approval never

# 2. Restore RDS from latest snapshot
aws rds restore-db-cluster-from-snapshot \
  --db-cluster-identifier sybol-cluster \
  --snapshot-identifier <latest-snapshot-id> \
  --engine aurora-postgresql \
  --vpc-security-group-ids sg-rds123

# 3. Restore Lambda functions
./scripts/deploy-all-lambdas.sh

# 4. Restore API Gateway configuration
aws apigatewayv2 import-api \
  --body file://backups/api_configuration.json
```

#### Phase 2: Data Recovery (1-2 hours)

```bash
# 1. Verify RDS cluster is available
aws rds describe-db-clusters \
  --db-cluster-identifier sybol-cluster \
  --query 'DBClusters[0].Status'

# 2. Restore individual databases if needed
./scripts/restore-all-tenant-databases.sh

# 3. Restore secrets
./scripts/restore-secrets.sh secrets_backup_latest.json.encrypted

# 4. Verify database integrity
./scripts/verify-database-integrity.sh
```

#### Phase 3: Tenant Infrastructure Recovery (1 hour per tenant)

```bash
# For each tenant, restore:
# 1. CloudFront distribution
cd infraestructure/ClientInfra
cdk deploy -c tenantId=repsol

# 2. Frontend files
aws s3 sync s3://sybol-backups/frontend/repsol-latest/ \
  s3://repsol-staging-wallet-frontend/

# 3. Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id <dist-id> \
  --paths "/*"
```

#### Phase 4: Verification (30 minutes)

```bash
# 1. Run health checks
./scripts/health-check-all-services.sh

# 2. Test authentication
./scripts/test-authentication.sh

# 3. Test API endpoints
./scripts/test-api-endpoints.sh

# 4. Verify tenant access
./scripts/verify-tenant-access.sh repsol
```

### Regional Failover Procedure

If primary region (eu-west-1) fails, failover to replica region (us-east-1):

#### Update Route 53 Health Checks

```bash
# Disable primary region health check
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://failover-to-us-east-1.json
```

#### Promote Read Replica

```bash
# Promote replica to standalone cluster
aws rds promote-read-replica-db-cluster \
  --db-cluster-identifier sybol-cluster-replica-us-east-1 \
  --region us-east-1
```

#### Update Application Configuration

```bash
# Update Lambda environment variables to point to new region
for FUNCTION in backoffice businesslogic propagate catalog; do
  aws lambda update-function-configuration \
    --function-name $FUNCTION \
    --environment Variables="{
      DB_HOST=sybol-cluster-replica-us-east-1.cluster-xxxxx.us-east-1.rds.amazonaws.com,
      DB_PORT=5432,
      AWS_REGION=us-east-1
    }"
done
```

---

## Testing Backup and Recovery

### Monthly DR Drill

Execute monthly disaster recovery drills to validate procedures.

#### DR Drill Checklist

- [ ] Restore RDS cluster from snapshot to test environment
- [ ] Restore one tenant database from backup
- [ ] Restore Secrets Manager secrets
- [ ] Deploy Lambda functions from ECR
- [ ] Restore frontend from S3 backup
- [ ] Verify end-to-end functionality
- [ ] Document time taken for each step
- [ ] Update procedures based on findings

#### DR Drill Script

```bash
#!/bin/bash
# Script: disaster-recovery-drill.sh

echo "Starting DR Drill - $(date)"

# 1. Restore RDS to test cluster
echo "Step 1: Restoring RDS cluster..."
aws rds restore-db-cluster-from-snapshot \
  --db-cluster-identifier sybol-cluster-dr-test \
  --snapshot-identifier $(aws rds describe-db-cluster-snapshots \
    --db-cluster-identifier sybol-cluster \
    --snapshot-type automated \
    --query 'DBClusterSnapshots[0].DBClusterSnapshotIdentifier' \
    --output text)

# 2. Wait for cluster to be available
echo "Waiting for cluster to be available..."
aws rds wait db-cluster-available \
  --db-cluster-identifier sybol-cluster-dr-test

# 3. Test database connectivity
echo "Step 2: Testing database connectivity..."
psql -h sybol-cluster-dr-test.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -d catalog \
     -c "SELECT COUNT(*) FROM catalog_entries;"

# 4. Clean up
echo "Step 3: Cleaning up test resources..."
aws rds delete-db-cluster \
  --db-cluster-identifier sybol-cluster-dr-test \
  --skip-final-snapshot

echo "DR Drill completed - $(date)"
```

---

## Backup Monitoring

### CloudWatch Alarms for Backups

```bash
# Create alarm for backup failures
aws cloudwatch put-metric-alarm \
  --alarm-name rds-backup-failed \
  --alarm-description "Alert when RDS backup fails" \
  --metric-name BackupRetentionPeriodStorageUsed \
  --namespace AWS/RDS \
  --statistic Average \
  --period 86400 \
  --threshold 0 \
  --comparison-operator LessThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --dimensions Name=DBClusterIdentifier,Value=sybol-cluster \
  --alarm-actions arn:aws:sns:eu-west-1:ACCOUNT_ID:ops-critical
```

### Verify Backup Integrity

```bash
#!/bin/bash
# Script: verify-backups.sh

# Check RDS automated backups
LATEST_BACKUP=$(aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier sybol-cluster \
  --snapshot-type automated \
  --query 'DBClusterSnapshots[0].SnapshotCreateTime' \
  --output text)

echo "Latest RDS backup: $LATEST_BACKUP"

# Check S3 database backups
LATEST_DB_BACKUP=$(aws s3 ls s3://sybol-backups/databases/ --recursive | \
  sort | tail -n 1 | awk '{print $1, $2}')

echo "Latest database backup: $LATEST_DB_BACKUP"

# Check secrets backup
LATEST_SECRETS_BACKUP=$(aws s3 ls s3://sybol-backups/secrets/ | \
  sort | tail -n 1 | awk '{print $1, $2}')

echo "Latest secrets backup: $LATEST_SECRETS_BACKUP"

# Verify backup ages
# Add logic to alert if backups are older than expected
```

---

## References

- [Infrastructure Setup](infrastructure-setup.md)
- [Deployment Procedures](deployment-procedures.md)
- [Monitoring Guide](monitoring.md)
- [AWS RDS Backup Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html)
- [AWS Disaster Recovery](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html)
