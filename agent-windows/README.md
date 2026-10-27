# FIM Windows Agent

The FIM Windows Agent is a lightweight, low-footprint background Windows Service designed for Windows 10, Windows 11, and Windows Server (2016, 2019, 2022, 2025).

## Architecture & Subsystems

1. **`service/`**: Windows Service lifecycle coordinator managing daemon worker threads.
2. **`watcher/`**: Real-time filesystem observer using Windows kernel notifications (`ReadDirectoryChangesW`).
3. **`hashing/`**: Streaming chunked SHA-256 calculation engine with exponential retry for locked files.
4. **`baseline/`**: Recursive directory baseline scanner with local SQLite baseline cache and drift detection.
5. **`auditing/`**: Windows Security Event Log collector subscribing to Event IDs 4663, 4656, and 4670.
6. **`spool/`**: Transactional, crash-safe local SQLite spool database (`spool.db` in WAL mode) for zero data loss.
7. **`transport/`**: Authenticated HTTP transport client with batch event uploads and exponential backoff.
8. **`configuration/`**: Persistent agent configuration and credential manager.
9. **`diagnostics/`**: Real-time health metrics (CPU, memory, queue depth, disk usage).
10. **`installer/`**: Automated PowerShell deployment script (`install.ps1`).

---

## Quick Installation on Windows Client

Run an elevated PowerShell window (`Run as Administrator`):

```powershell
& ".\installer\install.ps1" -ServerUrl "http://<SERVER_IP>:8000" -EnrollmentToken "<YOUR_ENROLLMENT_TOKEN>"
```

For complete Group Policy (GPO) deployment and SACL configuration instructions, see [docs/WINDOWS_AGENT.md](../docs/WINDOWS_AGENT.md).
