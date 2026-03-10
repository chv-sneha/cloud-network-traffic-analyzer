import json
import boto3
import re
from datetime import datetime

# AWS clients
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

# Config
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:traffic-alerts'
HIGH_TRAFFIC_THRESHOLD = 1000
REJECTED_CONN_THRESHOLD = 100

def parse_flow_log(log_line):
    fields = log_line.strip().split()
    if len(fields) < 13:
        return None
    return {
        'version':      fields[0],
        'account_id':   fields[1],
        'interface_id': fields[2],
        'src_ip':       fields[3],
        'dst_ip':       fields[4],
        'src_port':     fields[5],
        'dst_port':     fields[6],
        'protocol':     fields[7],
        'packets':      int(fields[8]) if fields[8].isdigit() else 0,
        'bytes':        int(fields[9]) if fields[9].isdigit() else 0,
        'action':       fields[12],
    }

def detect_anomalies(logs):
    anomalies = []
    rejected_count = 0
    total_bytes = 0
    ip_traffic = {}

    for log in logs:
        entry = parse_flow_log(log)
        if not entry:
            continue

        total_bytes += entry['bytes']

        # Count rejected connections
        if entry['action'] == 'REJECT':
            rejected_count += 1

        # Track traffic per source IP
        src = entry['src_ip']
        ip_traffic[src] = ip_traffic.get(src, 0) + entry['bytes']

    # Rule 1: High traffic volume
    if total_bytes > HIGH_TRAFFIC_THRESHOLD:
        anomalies.append({
            'type': 'HIGH_TRAFFIC',
            'detail': f'Total bytes: {total_bytes} exceeded threshold {HIGH_TRAFFIC_THRESHOLD}'
        })

    # Rule 2: Too many rejected connections
    if rejected_count > REJECTED_CONN_THRESHOLD:
        anomalies.append({
            'type': 'HIGH_REJECTIONS',
            'detail': f'Rejected connections: {rejected_count} exceeded threshold {REJECTED_CONN_THRESHOLD}'
        })

    # Rule 3: Single IP sending too much traffic
    for ip, traffic in ip_traffic.items():
        if traffic > HIGH_TRAFFIC_THRESHOLD * 0.8:
            anomalies.append({
                'type': 'SUSPICIOUS_IP',
                'detail': f'IP {ip} sent {traffic} bytes — possible port scan or DDoS'
            })

    return anomalies

def send_alert(anomalies):
    message = f"""
🚨 NETWORK ANOMALY DETECTED
Time: {datetime.utcnow().isoformat()}
Anomalies Found: {len(anomalies)}

Details:
"""
    for a in anomalies:
        message += f"\n[{a['type']}] {a['detail']}"

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='🚨 Cloud Network Traffic Alert',
        Message=message
    )
    print("Alert sent via SNS!")

def lambda_handler(event, context):
    print("Traffic Analyzer Lambda started...")

    # Extract log da