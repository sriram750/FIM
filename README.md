# FIM Enterprise — Enterprise File Integrity Monitoring & Attribution

FIM Enterprise is a high-performance, self-hosted, distributed File Integrity Monitoring (FIM) platform designed for monitoring 500+ Windows client computers and Windows file servers across enterprise on-premises networks.

## Core Capabilities
- **Real-Time Filesystem Watching**: Monitors Windows directories for file creation, modification, deletion, and rename events using kernel notifications (`ReadDirectoryChangesW`) and NTFS USN Journal reconciliation.
- **Cryptographic Baseline Verification**: Computes streaming SHA-256 file hashes, maintaining baseline state records and detecting unauthorized drifts.
- **Windows User Attribution**: Forensically correlates filesystem change events with Windows Security Auditing (Event IDs 4663, 4656, 4670) to identify the actor account (SID, Domain\Username, Process Name) when evidence supports attribution, and indicates unknown attribution when evidence is absent.
- **Durable Local Spooling**: Windows endpoints buffer events locally in an ACID SQLite spool (`spool.db`), guaranteeing zero event loss during network partitions or server maintenance.
- **Enterprise Decoupled Pipeline**: Scalable ingestion through FastAPI, Redis Streams buffer, asynchronous Python workers, and OpenSearch indexing.
- **Cyber Defense Dashboard**: Built with React, TypeScript, Vite, Tailwind CSS, Lucide icons, and high-density telemetry views.

---

## Architecture Topology

- **Web / Ingress**: Nginx reverse proxy with TLS termination and API rate limiting.
- **Backend API**: FastAPI (Python 3.12) with Pydantic validation and SQLAlchemy 2.0.
- **Authoritative Database**: PostgreSQL 16 (storing users, endpoints, credentials, policies, baselines, alerts, audit logs).
- **Buffer / Queue**: Redis Streams 7.2 with consumer groups and acknowledgments.
- **Search & Analytics**: OpenSearch 2.11 for high-volume forensic search and indexing.
- **Worker**: Asynchronous event ingestion, alert rule evaluation, and OpenSearch sync worker.
- **Windows Agent**: Native Windows service with local durable spooling, streaming hasher, and Windows Security Event Log subscriber.

---

## Getting Started

### 1. Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Configure your secure passwords, secrets, and environment parameters.

### 2. Docker Compose Deployment
```bash
docker compose up -d --build
```
Check health:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/health
```

### 3. Local Development (Without Docker)

#### Backend:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173).

---

## License
Proprietary — Enterprise Cybersecurity Operations.
