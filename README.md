# 🌐 Cloud Network Traffic Analyzer

A cloud-based network monitoring system that captures, analyzes, 
and visualizes network traffic within a virtual AWS environment 
to detect unusual patterns and potential security threats.

---

## 🏗️ Architecture
```
VPC → VPC Flow Logs → CloudWatch Log Group
→ AWS Lambda Analyzer → Anomaly Detection
→ SNS Alert System → Grafana Dashboard
```

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
│   └── analyzer.py        # Anomaly detection Lambda function
├── grafana/
│   └── dashboard.json     # Grafana dashboard configuration
├── screenshots/           # AWS console proof of implementation
└── README.md
```

---

## 🚀 Deployment Steps

### 1. VPC + Flow Logs
- Create VPC with public/private subnets
- Enable VPC Flow Logs → CloudWatch Log Group

### 2. Lambda Analyzer
- Deploy `lambda/analyzer.py` to AWS Lambda
- Set CloudWatch Logs as trigger
- Attach IAM role with CloudWatch + SNS permissions

### 3. SNS Alerting
- Create SNS topic: `traffic-alerts`
- Subscribe your email
- Update `SNS_TOPIC_ARN` in `analyzer.py`

### 4. Grafana Dashboard
- Install Grafana
- Connect CloudWatch as data source
- Import `grafana/dashboard.json`

---

## 📸 Screenshots

| Component | Screenshot |
|---|---|
| VPC Flow Logs | ![Flow Logs](screenshots/vpc-flow-logs.png) |
| Lambda Running | ![Lambda](screenshots/lambda-running.png) |
| SNS Alert | ![SNS](screenshots/sns-alert.png) |
| Grafana Dashboard | ![Grafana](screenshots/grafana-dashboard.png) |

---

## 💡 Key Concepts Demonstrated

- Cloud networking & VPC architecture
- Serverless computing with AWS Lambda
- Log-based anomaly detection
- Real-time alerting pipelines
- Infrastructure observability

---

## ⚠️ Cleanup

To avoid AWS charges, delete these resources after demo:
1. VPC Flow Logs
2. CloudWatch Log Group
3. Lambda Function
4. SNS Topic
5. VPC
```

---

Save both files. Your VS Code folder should now look like this:
```
cloud-network-traffic-analyzer/
├── lambda/
│   └── analyzer.py       ✅
├── grafana/
│   └── dashboard.json    ✅
├── screenshots/          ✅ (empty for now)
├── .gitignore            ✅
└── README.md             ✅