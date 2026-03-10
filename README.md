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

## 🚀 Deployment Guide

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.9+
- Grafana (local or cloud instance)
- Basic understanding of AWS networking

### Architecture Components

This system consists of five main components:

1. **VPC with Flow Logs** - Captures all network traffic
2. **CloudWatch Log Group** - Stores and streams flow logs
3. **Lambda Function** - Analyzes traffic for anomalies
4. **SNS Topic** - Sends alert notifications
5. **Grafana Dashboard** - Visualizes traffic metrics

### Deployment Overview

The deployment process involves:
- Setting up VPC infrastructure with flow logs enabled
- Configuring CloudWatch for log aggregation
- Deploying Lambda function with anomaly detection logic
- Creating SNS topic for alerting
- Connecting Grafana to CloudWatch for visualization

For detailed deployment instructions, refer to the [architecture.md](architecture.md) file.

### Configuration

**Lambda Environment Variables:**
- `SNS_TOPIC_ARN` - ARN of the SNS topic for alerts
- `ANOMALY_THRESHOLD_PACKETS` - Packet threshold (default: 1000)
- `ANOMALY_THRESHOLD_REJECTS` - Reject threshold (default: 50)

**VPC Flow Logs Settings:**
- Traffic Type: ALL (accepted + rejected)
- Destination: CloudWatch Logs
- Log Format: Default AWS format
- Aggregation Interval: 1 minute

**IAM Permissions Required:**
- VPC Flow Logs: CloudWatch Logs write access
- Lambda: CloudWatch Logs read/write, SNS publish
- Grafana: CloudWatch read-only access

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

## 🧪 Testing & Validation

### Verify Deployment

1. **Check VPC Flow Logs**
   - Verify logs are streaming to CloudWatch
   - Confirm log format and data accuracy

2. **Test Lambda Function**
   - Monitor Lambda invocations in CloudWatch
   - Check execution logs for errors
   - Verify anomaly detection logic

3. **Validate SNS Alerts**
   - Confirm email subscription
   - Test alert delivery

4. **Review Grafana Dashboard**
   - Verify data source connection
   - Check metric visualization
   - Confirm real-time updates

### Generate Test Traffic

You can generate test traffic patterns to validate the system:

- **Normal Traffic**: Regular HTTP/HTTPS requests
- **High Volume**: Burst of concurrent connections
- **Port Scanning**: Sequential port access attempts
- **Rejected Connections**: Requests to blocked ports

Monitor the Grafana dashboard and email alerts to confirm detection.

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

## ⚠️ Resource Cleanup

To avoid ongoing AWS charges, remove all resources after testing:

### Cleanup Checklist

- [ ] Delete Lambda function
- [ ] Remove SNS topic and subscriptions
- [ ] Delete CloudWatch Log Group
- [ ] Disable and delete VPC Flow Logs
- [ ] Remove VPC and associated resources (subnets, route tables, etc.)
- [ ] Delete IAM roles and policies

**Important**: Delete resources in reverse order of creation to avoid dependency errors.

---

**Cloud Network Traffic Analyzer** - A professional AWS-based security monitoring solution