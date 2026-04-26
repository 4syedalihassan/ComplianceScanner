# CIS Compliance Scanner

Multi-environment CIS benchmarking and vulnerability assessment platform for continuous compliance visibility.

## Overview

Compliance Scanner provides unified security compliance scanning across:
- **AWS** - Agentless CIS benchmark scanning via Prowler + boto3 + SSM
- **Azure** - Azure CIS Foundations benchmarks
- **GCP** - GCP CIS Foundations benchmarks  
- **On-Premise** - Linux, Windows, Network devices, VMware
- **Kubernetes** - CIS Kubernetes benchmarks
- **Containers** - Container image scanning

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              LIGHTSAIL ($15/mo)                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │           Python FastAPI Server                   │  │
│  │  - Authentication + MFA                          │  │
│  │  - Scan Engine Dispatch                          │  │
│  │  - REST API                                      │  │
│  └─────────────────────────────────────────────────┘  │
│                         ↓                             │
│  ┌─────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                  │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- AWS Account (for AWS scanning)

### Setup

1. Clone the repository
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with your configuration
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Initialize database:
   ```bash
   psql -f src/database/schema.sql
   ```
6. Run the server:
   ```bash
   python -m uvicorn src.main:app --reload
   ```

### Docker

```bash
docker build -t cloud-aisle-scanner .
docker run -p 8000:8000 --env-file .env cloud-aisle-scanner
```

## Features

- **Multi-Cloud Scanning**: AWS, Azure, GCP
- **On-Premise Scanning**: Linux, Windows, Network, VMware
- **CIS Compliance**: Full CIS Benchmark coverage
- **MFA Security**: TOTP-based two-factor authentication
- **RBAC**: Role-based access control
- **Drift Detection**: Compare scan results over time
- **Automated Reports**: PDF generation with WeasyPrint
- **Notifications**: Email alerts on findings

## Project Structure

```
├── src/
│   ├── main.py              # FastAPI application
│   ├── auth/
│   │   └── mfa.py         # Authentication + MFA
│   ├── models/
│   │   └── __init__.py    # Data models
│   ├── database/
│   │   └── schema.sql     # Database schema
│   ├── scanners/
│   │   ├── aws/           # AWS scanners
│   │   ├── onprem/        # On-premise scanners
│   │   └── cloud/         # Azure, GCP scanners
│   └── api/
│       └── routes/         # API endpoints
├── docs/
│   ├── SPEC.md           # Full specification
│   └── database-schema.md
├── tests/
├── requirements.txt
└── Dockerfile
```

## API Endpoints

### Authentication
- `POST /auth/login` - Login
- `POST /auth/mfa-verify` - Verify MFA
- `POST /auth/mfa-setup` - Setup MFA

### Customers
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/{id}` - Get customer

### Scans
- `POST /api/customers/{id}/scan` - Trigger scan
- `GET /api/customers/{id}/scans` - List scans
- `GET /api/scans/{id}` - Get scan details

### Findings
- `GET /api/customers/{id}/findings` - List findings
- `PUT /api/findings/{id}/status` - Update status

## Cost

| Resource | Cost/Mo |
|----------|---------|
| Lightsail (2GB) | $15 |
| PostgreSQL 15 | included |
| S3 (reports) | ~$1 |
| **Total** | **~$16/mo** |

## License

Proprietary
