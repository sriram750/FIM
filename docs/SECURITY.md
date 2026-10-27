# FIM Enterprise — Security Architecture & Threat Model

## 1. Security Principles & Threat Mitigation

### 1.1 Zero-Trust Endpoint Architecture
- **Mutual Authentication**: Endpoints authenticate with unique cryptographically generated API tokens (`FIM-Endpoint-Key`) or mutual TLS client certificates.
- **No Shared Secrets**: No shared master secret or universal key is embedded in any agent build.
- **Revocation**: Administrative revocation of an endpoint token instantly invalidates its ability to push events or obtain policies.
- **Replay Protection**: Every event contains a monotonically increasing sequence number and a unique UUID. Duplicates are rejected at the database constraint level.

### 1.2 Authentication & Authorization (Web Platform)
- **Password Security**: Passwords hashed using **Argon2id** (`t=3, m=65536, p=4`), immune to GPU-based rainbow table and brute-force attacks.
- **Role-Based Access Control (RBAC)**:
  - `Admin`: Full system configuration, user management, policy updates, retention settings.
  - `Analyst`: View events, acknowledge/investigate alerts, download reports, view endpoints.
  - `Auditor`: Read-only access to audit logs, historical events, compliance reports.
- **Session Protection**:
  - Short-lived JWT access tokens (15 minutes).
  - Secure, HTTP-only, SameSite=Strict cookies for web sessions.
  - Revocable refresh tokens stored in PostgreSQL.
  - Strict Cross-Origin Resource Sharing (CORS) policy.

### 1.3 Threat Model (STRIDE)

| Threat Category | Potential Attack Vector | FIM Enterprise Countermeasure |
| :--- | :--- | :--- |
| **Spoofing** | Attacker impersonates an endpoint to inject fake events or clear alerts. | Unique endpoint credentials, sequence verification, HMAC signatures, IP origin tracking. |
| **Tampering** | Attacker modifies file event payload in transit or alters baseline. | TLS 1.3 in-transit encryption. Baseline hashes are server-authoritative and digitally tracked. |
| **Repudiation** | Attacker deletes file and claims legitimate activity or denies action. | Correlates Windows Security Event Log (Event ID 4663/4656) with filesystem event, recording actor SID and account. |
| **Information Disclosure** | Unauthorized user views file hashes or internal network topology. | Strict RBAC on all `/api/v1` routes; no public database/Redis/OpenSearch exposure; logs redact credentials. |
| **Denial of Service** | Malicious endpoint floods server with billions of file modification events. | Rate limiting per endpoint, batch size caps (max 500 events/batch), Redis Streams backpressure buffering. |
| **Elevation of Privilege** | Local attacker compromises Windows agent service or UI dashboard. | Windows agent operates as dedicated service account with minimal necessary privileges (SE_SECURITY_NAME for audit read). API strictly verifies role on every request. |

### 1.4 Windows Security Auditing & SACL Hardening
To attribute changes without excessive noise:
1. **Audit Policy**: Enable Advanced Audit Policy Configuration:
   - `Object Access` -> `Audit File System` (Success/Failure).
   - `Detailed Tracking` -> `Audit Process Creation` (Optional, enhances Process Name attribution).
2. **System Access Control Lists (SACL)**:
   - Only apply SACL to designated sensitive directories (e.g., `C:\Windows\System32\drivers\etc`, application data directories, financial databases).
   - Never place broad SACLs on `C:\Windows\Temp` or `%LOCALAPPDATA%` to prevent audit log flooding.

### 1.5 Secure Defaults
- No default admin password committed to version control.
- Non-root user execution in Docker containers.
- Database and search services bound to internal Docker bridge network (`fim-internal`), not mapped to host interfaces.
