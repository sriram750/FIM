# FIM Windows Agent

The FIM Windows Agent is a lightweight, low-footprint background Windows Service designed for Windows 10, Windows 11, and Windows Server (2016, 2019, 2022, 2025).

## Architecture & Subsystems

1. **`service/`**: Windows Service lifecycle manager (`Win32Service`), handling service start, stop, pause, and crash recovery.
2. **`watcher/`**: Filesystem change listener implementing `ReadDirectoryChangesW` with asynchronous I/O completion ports (IOCP), handling recursive monitoring, buffer overflows, and rename pairing.
3. **`hashing/`**: Streaming chunked SHA-256 calculation engine with file-lock retry exponential backoff.
4. **`baseline/`**: Initial and periodic filesystem scanner creating full baseline snapshots.
5. **`auditing/`**: Windows Security Event Log subscriber (`EvtSubscribe` / `ReadEventLog`) listening for Event IDs 4663, 4656, and 4670.
6. **`spool/`**: Durable, transactional SQLite local database (`spool.db`) with write-ahead logging (WAL) ensuring zero data loss during network disconnection.
7. **`transport/`**: Authenticated HTTPS batch client pushing events to `POST /api/v1/agents/events/batch` with sequence numbering and exponential backoff retry.
8. **`configuration/`**: Local policy cache and credential store with DPAPI encryption.
9. **`diagnostics/`**: Heartbeat and telemetry collector reporting CPU, memory, queue backlog, and watcher health.

## Installation & Deployment
Refer to `docs/WINDOWS_AGENT.md` for Group Policy (GPO) and SCCM deployment procedures.
