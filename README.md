# 🌐 Cloud Network Traffic Analyzer

A cloud-based network monitoring system that captures, analyzes, and visualizes network traffic within a virtual AWS environment to detect unusual patterns and potential security threats.

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange?logo=amazon-aws)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Lambda](https://img.shields.io/badge/Serverless-Lambda-yellow)](https://aws.amazon.com/lambda/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD                                  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                           VPC                                     │ │
│  │                                                                   │ │
│  │  ┌─────────────┐         ┌─────────────┐                        │ │
│  │  │   Public    │         │   Private   │                        │ │
│  │  │   Subnet    │         │   Subnet    │                        │ │
│  │  │             │         │             │                        │ │
│  │  │  EC2/ECS    │◄───────►│  Database   │                        │ │
│  │  │  Instances  │         │  Services   │                        │ │
│  │  └──────┬──────┘         └──────┬──────┘                        │ │
│  │         │                       │                                │ │
│  │         └───────────┬───────────┘                                │ │
│  │                     │                                            │ │
│  │              ┌──────▼──────┐                                     │ │
│  │              │ VPC Flow    │                                     │ │
│  │              │    Logs     │                                     │ │
│  │              └──────┬──────┘                                     │ │
│  └─────────────────────┼────────────────────────────────────────────┘ │
│                        │                                              │
│                        ▼                                              │
│              ┌─────────────────┐                                     │
│              │  CloudWatch     │                                     │
│              │   Log Group     │                                     │
│              │                 │                                     │
│              │ • Flow Records  │                                     │
│              │ • Timestamps    │                                     │
│              │ • IP Addresses  │                                     │
│              └────────┬────────┘                                     │
│                       │                                              │
│                       │ (Trigger)                                    │
│                       ▼                                              │
│              ┌─────────────────┐                                     │
│              │  AWS Lambda     │                                     │
│              │   (analyzer.py) │                                     │
│              │                 │                                     │
│              │ • Parse Logs    │                                     │
│              │ • Detect Anomaly│                                     │
│              │ • Analyze Traffic│                                    │
│              └────────┬────────┘                                     │
│                       │                                              │
│              ┌────────┴────────┐                                     │
│              │                 │                                     │
│              ▼                 ▼                                     │
│     ┌─────────────┐   ┌─────────────┐                              │
│     │  Amazon SNS │   │ CloudWatch  │                              │
│     │    Topic    │   │   Metrics   │                              │
│     │             │   │             │                              │
│     │ • Alerts    │   │ • Statistics│                              │
│     │ • Warnings  │   │ • Logs      │                              │
│     └──────┬──────┘   └──────┬──────┘                              │
│            │                 │                                      │
└────────────┼─────────────────┼──────────────────────────────────────┘
             │                 │
             ▼                 ▼
      ┌────────────┐    ┌────────────┐
      │   Email    │    │  Grafana   │
      │   Alert    │    │ Dashboard  │
      │            │    │            │
      │ 📧 Admin   │    │ 📊 Metrics │
      └────────────┘    └────────────┘
```

### Data Flow

1. **Traffic Capture**: VPC Flow Logs capture all network traffic (accepted/rejected connections)
2. **Log Aggregation**: Logs stream to CloudWatch Log Group in real-time
3. **Event Trigger**: New log entries trigger Lambda function automatically
4. **Analysis**: Lambda parses logs and applies anomaly detection algorithms
5. **Alerting**: Suspicious activity triggers SNS notifications
6. **Visualization**: Grafana queries CloudWatch for dashboard metrics

---

## ⚙️ Tech Stack

| Component | Technology |
|---|---|
| Cloud Provider | AWS |
| Network Monitoring | VPC Flow Logs |
| Log Storage | CloudWatch Logs |
| Anomaly Detection | AWS Lambda (Python) |
| Alerting | Amazon SNS |
| Visualization | Grafana |
| IaC | AWS Console + CLI |

---

## 🧠 Features

- **Real-time traffic monitoring** via VPC Flow Logs
- **Automated anomaly detection** — high traffic, rejected connections, suspicious IPs
- **Instant alerting** via SNS email notifications
- **Visual dashboards** showing traffic trends, accepted vs rejected traffic, top IPs

---

## 📁 Project Structure
```
cloud-network-traffic-analyzer/
├── lambda/
│   └── analyzer.py           # Anomaly detection Lambda function
├── grafana/
│   └── dashboard.json        # Grafana dashboard configuration
├── screenshots/              # AWS console proof of implementation
│   ├── vpc-flow-logs.png
│   ├── lambda-running.png
│   ├── sns-alert.png
│   └── grafana-dashboard.png
├── .gitignore
└── README.md                 # This file
```

---

## 🚀 Deployment Steps

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.9+
- Grafana installed (local or cloud)

### Step 1: Create VPC & Enable Flow Logs

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=TrafficAnalyzerVPC}]'

# Create CloudWatch Log Group
aws logs create-log-group --log-group-name /aws/vpc/flowlogs

# Enable VPC Flow Logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids <VPC_ID> \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs \
  --deliver-logs-permission-arn <IAM_ROLE_ARN>
```

### Step 2: Deploy Lambda Function

```bash
# Create IAM role for Lambda
aws iam create-role --role-name LambdaTrafficAnalyzer \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy --role-name LambdaTrafficAnalyzer \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

aws iam attach-role-policy --role-name LambdaTrafficAnalyzer \
  --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess

# Package and deploy Lambda
cd lambda
zip function.zip analyzer.py
aws lambda create-function \
  --function-name TrafficAnalyzer \
  --runtime python3.9 \
  --role <LAMBDA_ROLE_ARN> \
  --handler analyzer.lambda_handler \
  --zip-file fileb://function.zip
```

### Step 3: Configure SNS Alerts

```bash
# Create SNS topic
aws sns create-topic --name traffic-alerts

# Subscribe email
aws sns subscribe \
  --topic-arn <SNS_TOPIC_ARN> \
  --protocol email \
  --notification-endpoint your-email@example.com

# Update Lambda environment variable
aws lambda update-function-configuration \
  --function-name TrafficAnalyzer \
  --environment Variables={SNS_TOPIC_ARN=<SNS_TOPIC_ARN>}
```

### Step 4: Set CloudWatch Trigger

```bash
# Add CloudWatch Logs trigger to Lambda
aws logs put-subscription-filter \
  --log-group-name /aws/vpc/flowlogs \
  --filter-name LambdaTrigger \
  --filter-pattern "" \
  --destination-arn <LAMBDA_FUNCTION_ARN>
```

### Step 5: Setup Grafana Dashboard

1. Install Grafana CloudWatch plugin:
   ```bash
   grafana-cli plugins install cloudwatch
   ```

2. Add CloudWatch as data source in Grafana UI
3. Import `grafana/dashboard.json`
4. Configure AWS credentials with read access to CloudWatch

---

## 📸 Screenshots

| Component | Screenshot |
|---|---|
| VPC Flow Logs | ![Flow Logs](screenshots/vpc-flow-logs.png) |
| Lambda Running | ![Lambda](screenshots/lambda-running.png) |
| SNS Alert | ![SNS](screenshots/sns-alert.png) |
| Grafana Dashboard | ![Grafana](screenshots/grafana-dashboard.png) |

---

## 🔍 Anomaly Detection Logic

The Lambda function detects:

| Anomaly Type | Threshold | Action |
|---|---|---|
| High Traffic Volume | >1000 packets/min | SNS Alert |
| Rejected Connections | >50 rejects/min | SNS Alert |
| Suspicious IPs | Known malicious IPs | SNS Alert + Block |
| Port Scanning | >100 unique ports | SNS Alert |
| Unusual Protocol | Non-standard protocols | Log Warning |

## 💡 Key Concepts Demonstrated

- ☁️ **Cloud Networking**: VPC architecture with public/private subnets
- ⚡ **Serverless Computing**: Event-driven Lambda functions
- 🔍 **Log Analysis**: Real-time parsing and pattern detection
- 🚨 **Alerting Pipeline**: Automated SNS notifications
- 📊 **Observability**: Grafana dashboards for traffic visualization
- 🔐 **Security Monitoring**: Threat detection and anomaly identification

## 🧪 Testing

### Generate Test Traffic

```bash
# SSH into EC2 instance in VPC
ssh ec2-user@<EC2_PUBLIC_IP>

# Generate normal traffic
ping -c 100 8.8.8.8

# Simulate port scan (triggers anomaly)
nmap -p 1-1000 <TARGET_IP>

# Generate high volume traffic
for i in {1..2000}; do curl http://example.com; done
```

### Verify Alerts

1. Check email for SNS notifications
2. View Lambda logs: `aws logs tail /aws/lambda/TrafficAnalyzer --follow`
3. Monitor Grafana dashboard for traffic spikes

---

## 📊 Sample Metrics

```
Traffic Statistics (Last 24h):
├── Total Packets: 1,245,678
├── Accepted: 1,198,432 (96.2%)
├── Rejected: 47,246 (3.8%)
├── Unique IPs: 3,421
├── Anomalies Detected: 12
└── Alerts Sent: 5
```

## 🛠️ Troubleshooting

| Issue | Solution |
|---|---|
| Lambda not triggering | Check CloudWatch Logs subscription filter |
| No SNS emails | Confirm email subscription in SNS console |
| Missing flow logs | Verify IAM role has CloudWatch Logs permissions |
| Grafana no data | Check AWS credentials and CloudWatch data source |

## 📈 Future Enhancements

- [ ] Machine learning-based anomaly detection
- [ ] Integration with AWS GuardDuty
- [ ] Automated IP blocking via Security Groups
- [ ] Multi-region traffic analysis
- [ ] Cost optimization with S3 log archival
- [ ] Slack/Teams integration for alerts

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📄 License

MIT License - feel free to use this project for learning and portfolio purposes.

## ⚠️ Cleanup

To avoid AWS charges, delete these resources after demo:

```bash
# Delete Lambda function
aws lambda delete-function --function-name TrafficAnalyzer

# Delete SNS topic
aws sns delete-topic --topic-arn <SNS_TOPIC_ARN>

# Delete CloudWatch Log Group
aws logs delete-log-group --log-group-name /aws/vpc/flowlogs

# Delete VPC Flow Logs
aws ec2 delete-flow-logs --flow-log-ids <FLOW_LOG_ID>

# Delete VPC (after removing dependencies)
aws ec2 delete-vpc --vpc-id <VPC_ID>
```

---

**Built with ❤️ for cloud security and network monitoring**