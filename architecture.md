# 🏗️ System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AWS CLOUD (us-east-1)                               │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                              VPC (10.0.0.0/16)                        │  │
│  │                                                                       │  │
│  │  ┌──────────────────┐              ┌──────────────────┐             │  │
│  │  │  Public Subnet   │              │  Private Subnet  │             │  │
│  │  │  10.0.1.0/24     │              │  10.0.2.0/24     │             │  │
│  │  │                  │              │                  │             │  │
│  │  │  ┌────────────┐  │              │  ┌────────────┐ │             │  │
│  │  │  │ EC2/ECS    │  │◄────────────►│  │  RDS/DB    │ │             │  │
│  │  │  │ Instances  │  │              │  │  Services  │ │             │  │
│  │  │  └────────────┘  │              │  └────────────┘ │             │  │
│  │  │                  │              │                  │             │  │
│  │  │  ┌────────────┐  │              │  ┌────────────┐ │             │  │
│  │  │  │   NAT GW   │  │              │  │  Lambda    │ │             │  │
│  │  │  └────────────┘  │              │  │  (VPC)     │ │             │  │
│  │  └──────────────────┘              └──────────────────┘             │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │                    VPC Flow Logs                                 │ │  │
│  │  │  • Captures ALL network traffic (accepted/rejected)              │ │  │
│  │  │  • Source/Destination IPs, Ports, Protocols                      │ │  │
│  │  │  • Bytes transferred, Packets, Action (ACCEPT/REJECT)            │ │  │
│  │  └─────────────────────────────┬───────────────────────────────────┘ │  │
│  └────────────────────────────────┼─────────────────────────────────────┘  │
│                                   │                                        │
│                                   ▼                                        │
│                  ┌─────────────────────────────────┐                       │
│                  │    CloudWatch Log Group         │                       │
│                  │  /aws/vpc/flowlogs              │                       │
│                  │                                 │                       │
│                  │  Log Format:                    │                       │
│                  │  <version> <account-id>         │                       │
│                  │  <interface-id> <srcaddr>       │                       │
│                  │  <dstaddr> <srcport> <dstport>  │                       │
│                  │  <protocol> <packets> <bytes>   │                       │
│                  │  <start> <end> <action> <status>│                       │
│                  └────────────────┬────────────────┘                       │
│                                   │                                        │
│                                   │ (Event Trigger)                        │
│                                   ▼                                        │
│                  ┌─────────────────────────────────┐                       │
│                  │      AWS Lambda Function        │                       │
│                  │      TrafficAnalyzer            │                       │
│                  │      Runtime: Python 3.9        │                       │
│                  │                                 │                       │
│                  │  ┌───────────────────────────┐  │                       │
│                  │  │  Anomaly Detection Logic  │  │                       │
│                  │  │                           │  │                       │
│                  │  │  ✓ High Traffic Volume    │  │                       │
│                  │  │    (>1000 packets/min)    │  │                       │
│                  │  │                           │  │                       │
│                  │  │  ✓ Rejected Connections   │  │                       │
│                  │  │    (>50 rejects/min)      │  │                       │
│                  │  │                           │  │                       │
│                  │  │  ✓ Suspicious IP Patterns │  │                       │
│                  │  │    (Known malicious IPs)  │  │                       │
│                  │  │                           │  │                       │
│                  │  │  ✓ Port Scanning Activity │  │                       │
│                  │  │    (>100 unique ports)    │  │                       │
│                  │  │                           │  │                       │
│                  │  │  ✓ Unusual Protocols      │  │                       │
│                  │  │    (Non-standard traffic) │  │                       │
│                  │  └───────────────────────────┘  │                       │
│                  └────────────────┬────────────────┘                       │
│                                   │                                        │
│                    ┌──────────────┴──────────────┐                         │
│                    │                             │                         │
│                    ▼                             ▼                         │
│         ┌──────────────────┐      ┌──────────────────┐                    │
│         │   Amazon SNS     │      │   CloudWatch     │                    │
│         │   Topic          │      │   Metrics        │                    │
│         │ traffic-alerts   │      │                  │                    │
│         │                  │      │  • Custom Metrics│                    │
│         │ • Email Protocol │      │  • Logs Insights │                    │
│         │ • SMS Protocol   │      │  • Dashboards    │                    │
│         │ • Lambda Hook    │      │  • Alarms        │                    │
│         └────────┬─────────┘      └────────┬─────────┘                    │
│                  │                         │                              │
└──────────────────┼─────────────────────────┼──────────────────────────────┘
                   │                         │
                   ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │  Email Alert     │      │  Grafana         │
        │  📧 Admin        │      │  Dashboard       │
        │                  │      │                  │
        │  Subject:        │      │  📊 Panels:      │
        │  "⚠️ Traffic     │      │  • Traffic Volume│
        │   Anomaly"       │      │  • Accept/Reject │
        │                  │      │  • Top IPs       │
        │  Body:           │      │  • Anomaly Count │
        │  • Timestamp     │      │  • Protocol Dist │
        │  • Anomaly Type  │      │  • Geo Map       │
        │  • Source IP     │      │                  │
        │  • Details       │      │  Refresh: 30s    │
        └──────────────────┘      └──────────────────┘
```

---

## 🔄 Data Flow Sequence

### Step-by-Step Process

```
1. TRAFFIC GENERATION
   └─► EC2/ECS instances generate network traffic
       └─► Inbound/Outbound connections
           └─► TCP/UDP/ICMP protocols

2. TRAFFIC CAPTURE
   └─► VPC Flow Logs capture every network interface transaction
       └─► Records: Source IP, Dest IP, Ports, Protocol, Action
           └─► Sampling: ALL traffic (no sampling)

3. LOG AGGREGATION
   └─► Flow logs stream to CloudWatch Log Group
       └─► Real-time ingestion (< 1 minute delay)
           └─► Retention: 7 days (configurable)

4. EVENT TRIGGERING
   └─► CloudWatch Logs Subscription Filter
       └─► Triggers Lambda on new log entries
           └─► Batch size: 100 records per invocation

5. ANALYSIS & DETECTION
   └─► Lambda function processes log batch
       └─► Parses VPC Flow Log format
           └─► Applies anomaly detection rules
               └─► Aggregates statistics

6. ALERTING
   └─► If anomaly detected:
       └─► Publish message to SNS topic
           └─► Email notification sent
               └─► CloudWatch metric recorded

7. VISUALIZATION
   └─► Grafana queries CloudWatch
       └─► Displays real-time metrics
           └─► Historical trend analysis
```

---

## 🧩 Component Details

### 1. VPC Flow Logs

**Purpose**: Capture network traffic metadata

**Configuration**:
- Traffic Type: `ALL` (accepted + rejected)
- Destination: CloudWatch Logs
- Log Format: Default (14 fields)
- Aggregation Interval: 1 minute

**Sample Log Entry**:
```
2 123456789012 eni-1a2b3c4d 172.31.16.139 172.31.16.21 20641 22 6 20 4249 1418530010 1418530070 ACCEPT OK
```

**Fields**:
- `version`: 2
- `account-id`: AWS account
- `interface-id`: ENI identifier
- `srcaddr`: Source IP
- `dstaddr`: Destination IP
- `srcport`: Source port
- `dstport`: Destination port
- `protocol`: IANA protocol number (6=TCP, 17=UDP)
- `packets`: Number of packets
- `bytes`: Number of bytes
- `start`: Start timestamp
- `end`: End timestamp
- `action`: ACCEPT or REJECT
- `log-status`: OK, NODATA, SKIPDATA

---

### 2. CloudWatch Log Group

**Purpose**: Centralized log storage and streaming

**Configuration**:
- Log Group: `/aws/vpc/flowlogs`
- Retention: 7 days
- Encryption: AES-256 (default)

**Features**:
- Real-time log streaming
- Subscription filters for Lambda triggers
- CloudWatch Logs Insights for querying
- Metric filters for custom metrics

---

### 3. AWS Lambda Function

**Purpose**: Serverless anomaly detection engine

**Configuration**:
- Function Name: `TrafficAnalyzer`
- Runtime: Python 3.9
- Memory: 256 MB
- Timeout: 60 seconds
- Trigger: CloudWatch Logs

**Environment Variables**:
```bash
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:traffic-alerts
ANOMALY_THRESHOLD_PACKETS=1000
ANOMALY_THRESHOLD_REJECTS=50
```

**IAM Permissions**:
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`
- `sns:Publish`
- `cloudwatch:PutMetricData`

**Detection Algorithms**:

| Algorithm | Description | Threshold |
|-----------|-------------|-----------|
| Volume Spike | Detects sudden traffic increases | >1000 packets/min |
| Reject Rate | High connection rejection rate | >50 rejects/min |
| IP Reputation | Checks against known malicious IPs | Blacklist match |
| Port Scan | Multiple port access from single IP | >100 unique ports |
| Protocol Anomaly | Unusual protocol usage | Non-TCP/UDP/ICMP |

---

### 4. Amazon SNS

**Purpose**: Multi-channel alerting system

**Configuration**:
- Topic Name: `traffic-alerts`
- Protocol: Email
- Endpoint: `<admin-email>`

**Alert Format**:
```json
{
  "AlarmName": "High Traffic Anomaly",
  "Timestamp": "2024-01-15T10:30:00Z",
  "AnomalyType": "HIGH_TRAFFIC_VOLUME",
  "SourceIP": "203.0.113.45",
  "DestinationIP": "10.0.1.25",
  "PacketCount": 1523,
  "Action": "ACCEPT",
  "Severity": "HIGH"
}
```

---

### 5. Grafana Dashboard

**Purpose**: Real-time traffic visualization

**Data Source**: CloudWatch

**Panels**:
1. **Traffic Volume** (Time Series)
   - Metric: `NetworkPackets`
   - Aggregation: Sum per minute

2. **Accept vs Reject** (Pie Chart)
   - Metric: `ConnectionAction`
   - Dimensions: ACCEPT, REJECT

3. **Top Source IPs** (Table)
   - Query: Top 10 IPs by packet count

4. **Anomaly Timeline** (Bar Chart)
   - Metric: `AnomalyDetected`
   - Type: High Traffic, Port Scan, etc.

5. **Protocol Distribution** (Donut Chart)
   - Breakdown: TCP, UDP, ICMP, Other

6. **Geographic Map** (World Map)
   - IP geolocation visualization

**Refresh Rate**: 30 seconds

---

## 🔐 Security Architecture

### IAM Roles & Policies

**VPC Flow Logs Role**:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ],
    "Resource": "arn:aws:logs:*:*:*"
  }]
}
```

**Lambda Execution Role**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:*:*:traffic-alerts"
    },
    {
      "Effect": "Allow",
      "Action": "cloudwatch:PutMetricData",
      "Resource": "*"
    }
  ]
}
```

### Network Security

- **VPC Isolation**: Private subnets for sensitive resources
- **Security Groups**: Least privilege access rules
- **NACLs**: Subnet-level traffic filtering
- **Encryption**: Data encrypted at rest and in transit

---

## 📊 Scalability & Performance

### Throughput Capacity

| Component | Capacity | Limit |
|-----------|----------|-------|
| VPC Flow Logs | Unlimited | No throttling |
| CloudWatch Logs | 5 MB/sec per stream | Soft limit |
| Lambda Concurrency | 1000 concurrent | Account limit |
| SNS | 30,000 msg/sec | Regional limit |

### Cost Optimization

**Estimated Monthly Cost** (for 1M packets/day):
- VPC Flow Logs: $0.50/GB ingested (~$15/month)
- CloudWatch Logs: $0.50/GB stored (~$10/month)
- Lambda: $0.20 per 1M requests (~$6/month)
- SNS: $0.50 per 1M notifications (~$1/month)

**Total**: ~$32/month

---

## 🔄 Disaster Recovery

### Backup Strategy
- CloudWatch Logs: 7-day retention
- Lambda Code: Versioned in S3
- Configuration: Infrastructure as Code (Terraform/CloudFormation)

### High Availability
- Multi-AZ VPC deployment
- Lambda: Automatic failover
- SNS: Multi-region replication

---

## 📈 Monitoring & Observability

### Key Metrics

1. **Lambda Metrics**:
   - Invocations
   - Duration
   - Errors
   - Throttles

2. **CloudWatch Metrics**:
   - IncomingLogEvents
   - IncomingBytes
   - DeliveryErrors

3. **Custom Metrics**:
   - AnomaliesDetected
   - AlertsSent
   - ProcessingLatency

### Alarms

- Lambda error rate > 5%
- CloudWatch log delivery failures
- SNS delivery failures
- High Lambda duration (> 30s)

---

## 🌐 Network Topology

```
                    ┌─────────────────┐
                    │    Internet     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Internet Gateway│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        │              VPC (10.0.0.0/16)          │
        │                    │                    │
        │    ┌───────────────┴───────────────┐    │
        │    │                               │    │
        │    ▼                               ▼    │
        │ ┌─────────────────┐    ┌─────────────────┐
        │ │ Public Subnet   │    │ Public Subnet   │
        │ │ 10.0.1.0/24     │    │ 10.0.3.0/24     │
        │ │ AZ: us-east-1a  │    │ AZ: us-east-1b  │
        │ │                 │    │                 │
        │ │ ┌─────────────┐ │    │ ┌─────────────┐ │
        │ │ │ Web Server  │ │    │ │ Web Server  │ │
        │ │ │ EC2/ECS     │ │    │ │ EC2/ECS     │ │
        │ │ └─────────────┘ │    │ └─────────────┘ │
        │ │                 │    │                 │
        │ │ ┌─────────────┐ │    │ ┌─────────────┐ │
        │ │ │  NAT GW     │ │    │ │  NAT GW     │ │
        │ │ │  (HA)       │ │    │ │  (HA)       │ │
        │ │ └──────┬──────┘ │    │ └──────┬──────┘ │
        │ └────────┼────────┘    └────────┼────────┘
        │          │                      │
        │          ▼                      ▼
        │ ┌─────────────────┐    ┌─────────────────┐
        │ │ Private Subnet  │    │ Private Subnet  │
        │ │ 10.0.2.0/24     │    │ 10.0.4.0/24     │
        │ │ AZ: us-east-1a  │    │ AZ: us-east-1b  │
        │ │                 │    │                 │
        │ │ ┌─────────────┐ │    │ ┌─────────────┐ │
        │ │ │ App Server  │ │    │ │ App Server  │ │
        │ │ │ Lambda/ECS  │◄┼────┼►│ Lambda/ECS  │ │
        │ │ └─────────────┘ │    │ └─────────────┘ │
        │ │                 │    │                 │
        │ │ ┌─────────────┐ │    │ ┌─────────────┐ │
        │ │ │ RDS Primary │◄┼────┼►│ RDS Standby │ │
        │ │ │ (Multi-AZ)  │ │    │ │ (Multi-AZ)  │ │
        │ │ └─────────────┘ │    │ └─────────────┘ │
        │ └─────────────────┘    └─────────────────┘
        │                                           │
        └───────────────────────────────────────────┘

        Route Tables:
        ┌─────────────────────────────────────────┐
        │ Public RT: 0.0.0.0/0 → IGW             │
        │ Private RT: 0.0.0.0/0 → NAT Gateway    │
        └─────────────────────────────────────────┘
```

## 🔀 Traffic Flow Patterns

### Inbound Traffic (Internet → VPC)
```
User Request
    ↓
Internet Gateway
    ↓
Public Subnet (Web Tier)
    ↓
Private Subnet (App Tier)
    ↓
Private Subnet (Database Tier)
    ↓
VPC Flow Logs Capture
```

### Outbound Traffic (VPC → Internet)
```
Private Subnet Resource
    ↓
NAT Gateway (Public Subnet)
    ↓
Internet Gateway
    ↓
Internet
    ↓
VPC Flow Logs Capture
```

### Internal Traffic (VPC → VPC)
```
EC2 Instance (Public)
    ↓
Security Group Rules
    ↓
RDS Instance (Private)
    ↓
VPC Flow Logs Capture
```

---

## 🎯 Use Cases

### 1. DDoS Attack Detection
**Scenario**: Sudden spike in traffic from multiple IPs
```
Detection:
- Packet count > 10,000/min from single IP
- Multiple source IPs targeting single destination
- High reject rate (>80%)

Response:
- SNS alert to security team
- Auto-block via Security Group update
- CloudWatch alarm triggers
```

### 2. Port Scanning Detection
**Scenario**: Attacker probing for open ports
```
Detection:
- Single IP accessing >100 unique ports
- Sequential port access pattern
- High reject rate on uncommon ports

Response:
- Immediate SNS alert
- Log IP to threat database
- Grafana dashboard highlights activity
```

### 3. Data Exfiltration Detection
**Scenario**: Unusual outbound data transfer
```
Detection:
- Bytes transferred > 10GB in 5 minutes
- Outbound traffic to unknown IPs
- Non-business hours activity

Response:
- Critical SNS alert
- Lambda triggers investigation workflow
- Automated traffic blocking
```

### 4. Compliance Monitoring
**Scenario**: Audit trail for network access
```
Use:
- Track all database access attempts
- Monitor rejected connections
- Generate compliance reports

Benefit:
- SOC 2 compliance evidence
- PCI-DSS network monitoring
- HIPAA audit trails
```

---

## 🧪 Testing Scenarios

### Test 1: Normal Traffic Baseline
```bash
# Generate normal HTTP traffic
for i in {1..100}; do
  curl -s http://example.com > /dev/null
  sleep 1
done

Expected: No alerts, normal metrics in Grafana
```

### Test 2: High Volume Attack
```bash
# Simulate traffic spike
for i in {1..2000}; do
  curl -s http://target-ip &
done

Expected: SNS alert "High Traffic Volume Detected"
```

### Test 3: Port Scan Simulation
```bash
# Scan ports 1-1000
nmap -p 1-1000 target-ip

Expected: SNS alert "Port Scanning Detected"
```

### Test 4: Rejected Connections
```bash
# Attempt connections to blocked ports
for port in {8000..8100}; do
  nc -zv target-ip $port 2>&1
done

Expected: SNS alert "High Reject Rate"
```

---

## 📊 Sample CloudWatch Queries

### Query 1: Top Talkers (Most Active IPs)
```sql
fields @timestamp, srcaddr, dstaddr, bytes
| stats sum(bytes) as total_bytes by srcaddr
| sort total_bytes desc
| limit 10
```

### Query 2: Rejected Connections
```sql
fields @timestamp, srcaddr, dstaddr, srcport, dstport, action
| filter action = "REJECT"
| stats count() by srcaddr
| sort count desc
```

### Query 3: Traffic by Protocol
```sql
fields @timestamp, protocol, bytes
| stats sum(bytes) as total by protocol
| sort total desc
```

### Query 4: Anomaly Timeline
```sql
fields @timestamp, srcaddr, packets
| filter packets > 1000
| sort @timestamp desc
```

---

## 🔧 Advanced Configuration

### Custom VPC Flow Log Format
```bash
# Enhanced format with additional fields
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxxxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs \
  --log-format '${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-status} ${vpc-id} ${subnet-id} ${instance-id} ${tcp-flags} ${type} ${pkt-srcaddr} ${pkt-dstaddr}'
```

### Lambda Environment Variables
```bash
# Configure thresholds
aws lambda update-function-configuration \
  --function-name TrafficAnalyzer \
  --environment Variables="{
    SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:traffic-alerts,
    THRESHOLD_PACKETS=1000,
    THRESHOLD_REJECTS=50,
    THRESHOLD_PORTS=100,
    BLACKLIST_IPS='203.0.113.0/24,198.51.100.0/24',
    ALERT_EMAIL=admin@example.com,
    ENABLE_AUTO_BLOCK=true
  }"
```

### CloudWatch Metric Filters
```bash
# Create metric for rejected connections
aws logs put-metric-filter \
  --log-group-name /aws/vpc/flowlogs \
  --filter-name RejectedConnections \
  --filter-pattern '[version, account, eni, source, destination, srcport, destport, protocol, packets, bytes, windowstart, windowend, action=REJECT, flowlogstatus]' \
  --metric-transformations \
    metricName=RejectedConnectionCount,\
    metricNamespace=VPC/Traffic,\
    metricValue=1
```

---

## 🚀 Performance Optimization

### Lambda Optimization
```python
# Use connection pooling
import boto3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_sns_client():
    return boto3.client('sns')

# Batch processing
def process_logs_batch(records, batch_size=100):
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        analyze_batch(batch)
```

### CloudWatch Logs Optimization
```bash
# Set appropriate retention
aws logs put-retention-policy \
  --log-group-name /aws/vpc/flowlogs \
  --retention-in-days 7

# Export old logs to S3 for archival
aws logs create-export-task \
  --log-group-name /aws/vpc/flowlogs \
  --from 1609459200000 \
  --to 1612137600000 \
  --destination s3-bucket-name \
  --destination-prefix vpc-flow-logs/
```

---

## 📈 Grafana Dashboard Queries

### Panel 1: Traffic Volume Over Time
```
Metric: NetworkPackets
Statistic: Sum
Period: 1 minute
Dimensions: VPC-ID
```

### Panel 2: Top 10 Source IPs
```
Query: 
fields srcaddr, sum(packets) as total
| stats sum(packets) by srcaddr
| sort total desc
| limit 10
```

### Panel 3: Accept/Reject Ratio
```
Metric: ConnectionAction
Statistic: Sum
Dimensions: Action (ACCEPT/REJECT)
Visualization: Pie Chart
```

### Panel 4: Geographic Distribution
```
Query: 
fields srcaddr, geo_ip(srcaddr) as location
| stats count() by location
Visualization: World Map
```

---

## 🔐 Security Best Practices

### 1. Least Privilege IAM
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "logs:PutLogEvents"
    ],
    "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/vpc/flowlogs:*"
  }]
}
```

### 2. Encryption at Rest
```bash
# Enable KMS encryption for CloudWatch Logs
aws logs associate-kms-key \
  --log-group-name /aws/vpc/flowlogs \
  --kms-key-id arn:aws:kms:us-east-1:123456789012:key/xxxxx
```

### 3. VPC Endpoints
```bash
# Create VPC endpoint for CloudWatch Logs
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxx \
  --service-name com.amazonaws.us-east-1.logs \
  --route-table-ids rtb-xxxxx
```

### 4. Network Segmentation
- Isolate database tier in private subnets
- Use Security Groups for micro-segmentation
- Implement NACLs for subnet-level filtering
- Enable VPC Flow Logs on all ENIs

---

## 💰 Cost Analysis

### Monthly Cost Breakdown (1M packets/day)

| Service | Usage | Unit Cost | Monthly Cost |
|---------|-------|-----------|-------------|
| VPC Flow Logs | 30 GB/month | $0.50/GB | $15.00 |
| CloudWatch Logs Storage | 20 GB/month | $0.50/GB | $10.00 |
| Lambda Invocations | 30K/month | $0.20/1M | $0.01 |
| Lambda Duration | 1.5M GB-sec | $0.0000166667/GB-sec | $0.25 |
| SNS Notifications | 100/month | $0.50/1M | $0.01 |
| CloudWatch Metrics | 10 custom | $0.30/metric | $3.00 |
| Data Transfer | 5 GB/month | $0.09/GB | $0.45 |
| **TOTAL** | | | **$28.72** |

### Cost Optimization Tips
1. Reduce log retention to 3 days: Save $5/month
2. Filter logs before CloudWatch: Save $7/month
3. Use S3 for long-term storage: Save $8/month
4. Batch Lambda invocations: Save $0.10/month

---

## 🎓 Learning Resources

### AWS Documentation
- [VPC Flow Logs Guide](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)

### Related Projects
- AWS GuardDuty for threat detection
- AWS Security Hub for centralized security
- AWS Network Firewall for advanced filtering

---

**Architecture Version**: 2.0  
**Last Updated**: 2024  
**Region**: us-east-1  
**Maintained By**: Cloud Security Team  
**License**: MIT
