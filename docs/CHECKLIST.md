# FIM Enterprise — Development and Execution Checklist

## Phase 0: Inspect and Plan
- [x] Inspect workspace and development tools (Python 3.12, Node 24, npm 11, Docker Compose).
- [x] Create `docs/ARCHITECTURE.md`.
- [x] Create `docs/SECURITY.md`.
- [x] Create `docs/CHECKLIST.md`.
- [x] Define environment configuration `.env.example` and `.gitignore`.

## Phase 1: Foundation
- [ ] Create repository directory tree (`backend`, `frontend`, `agent-windows`, `worker`, `deploy`, `tests`, `docs`).
- [ ] Implement Docker Compose architecture (`docker-compose.yml`) with internal networking and persistent volumes.
- [ ] Implement Nginx reverse proxy configuration with TLS/HTTPS proxying.
- [ ] Implement Backend FastAPI core (`backend/app/core/config.py`, `logging.py`).
- [ ] Implement SQLAlchemy 2.0 Async database session and engine.
- [ ] Implement all 24 PostgreSQL database models in `backend/app/models/`.
- [ ] Implement Alembic migrations setup and initial schema migration.
- [ ] Implement FastAPI `/api/v1/health` and system status endpoints.
- [ ] Implement Frontend shell in React + TypeScript + Vite + Tailwind CSS.
- [ ] Add backend automated smoke tests and run them.
- [ ] Verify health endpoints and database connectivity.

## Phase 2: Authentication & Endpoint Registration
- [ ] Implement User model, Argon2id password hashing, and JWT token issuance.
- [ ] Implement `/api/v1/auth/login`, `/logout`, `/me`.
- [ ] Implement RBAC middleware and dependency injection (`require_permission`).
- [ ] Implement Endpoint enrollment API (`/api/v1/agents/enroll`) with secure enrollment tokens.
- [ ] Implement Endpoint inventory API (`/api/v1/agents`, `/api/v1/agents/{id}`).
- [ ] Implement Agent heartbeat and status tracking (`/api/v1/agents/heartbeat`).
- [ ] Add unit and integration tests for authentication and endpoint registration.

## Phase 3: Real Windows Agent
- [ ] Implement Windows filesystem watcher using `ReadDirectoryChangesW` / Python `watchdog`.
- [ ] Implement SHA-256 streaming file hasher with retry logic for locked files.
- [ ] Implement durable local spool using SQLite (`spool.db`) with transactional durability.
- [ ] Implement event normalizer (`file_created`, `file_modified`, `file_deleted`, `file_renamed`).
- [ ] Implement authenticated HTTPS batch transport with exponential backoff and jitter.
- [ ] Implement Agent health & heartbeat reporter.
- [ ] Test agent against real Windows filesystem directory.

## Phase 4: File Integrity Baselines & Recovery
- [ ] Implement baseline scan engine (`baseline_created`, `integrity_mismatch`).
- [ ] Implement periodic reconciliation against recorded state.
- [ ] Implement watcher overflow detection and reconciliation rescan.
- [ ] Implement rename correlation handling.
- [ ] Test interrupted monitoring and recovery.

## Phase 5: Windows User Attribution & Audit Correlation
- [ ] Implement Windows Security Event Log subscriber (Event IDs 4663, 4656, 4670).
- [ ] Implement correlation engine matching file events with Security audit records.
- [ ] Implement attribution confidence grading (`CONFIRMED`, `PROBABLE`, `AMBIGUOUS`, `UNKNOWN`).
- [ ] Document SACL configuration and Group Policy deployment.
- [ ] Test correlation with real file modifications.

## Phase 6: OpenSearch & Background Processing
- [ ] Implement Redis Streams consumer worker (`worker/app/main.py`).
- [ ] Implement OpenSearch index mappings and index template.
- [ ] Implement asynchronous indexing outbox worker.
- [ ] Implement reindexing and consistency checker between PostgreSQL and OpenSearch.
- [ ] Implement queue metrics and lag tracking.

## Phase 7: Web Dashboard & Alert Engine
- [ ] Build Enterprise Cyber Defense UI:
  - Overview Dashboard with high-density metrics and trend charts.
  - Endpoint Management with search, filter, and detail view.
  - Monitoring Policy editor and path configuration.
  - File Integrity Explorer with baseline vs. current hash diff.
  - Event Explorer with AG Grid, multi-filter, and CSV export.
  - Alerts & Investigations console with triage workflow.
  - Compliance Reports and audit log viewer.
  - Administration & User Management.
- [ ] Implement Alert Engine with rules (ransomware detection, executable tampering, baseline mismatch).
- [ ] Connect all frontend components to real backend API endpoints.

## Phase 8: Hardening, Testing & Documentation
- [ ] Comprehensive unit, integration, and load tests.
- [ ] Backup and disaster recovery scripts.
- [ ] Deployment, operations, and troubleshooting guides.
