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
Internet Gateway
       │
       ▼
┌──────────────────────────────────────┐
│         Public Subnet                │
│         10.0.1.0/24                  │
│                                      │
│  ┌──────────┐      ┌──────────┐     │
│  │  Web     │      │   NAT    │     │
│  │  Server  │      │  Gateway │     │
│  └──────────┘      └────┬─────┘     │
└──────────────────────────┼───────────┘
                           │
                           ▼
┌──────────────────────────────────────┐
│         Private Subnet               │
│         10.0.2.0/24                  │
│                                      │
│  ┌──────────┐      ┌──────────┐     │
│  │   App    │      │  Database│     │
│  │  Server  │◄────►│   (RDS)  │     │
│  └──────────┘      └──────────┘     │
└──────────────────────────────────────┘
```

---

**Architecture Version**: 1.0  
**Last Updated**: 2024  
**Region**: us-east-1  
**Maintained By**: Cloud Security Team
