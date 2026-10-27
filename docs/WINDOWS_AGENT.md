# FIM Enterprise — Windows Agent Installation & Deployment Guide

This guide describes how to install, enroll, and operate the **FIM Enterprise Windows Agent** on Windows client endpoints (Windows 10, Windows 11) and Windows Server systems (2016, 2019, 2022, 2025).

---

## 1. Prerequisites

1. **Operating System**: Windows 10/11 (64-bit) or Windows Server 2016+.
2. **Network Connectivity**: HTTPS/HTTP access to the central FIM Enterprise server (e.g., `http://<server-ip>:8000` or `https://fim.corp.local:8443`).
3. **Privileges**: Local Administrator privileges on the client machine.
4. **Python**: Python 3.10+ installed on the client machine.

---

## 2. Quick Installation (Automated PowerShell Script)

Run an elevated PowerShell window (`Run as Administrator`) on the Windows client machine:

```powershell
# 1. Clone or copy the agent-windows folder to the client machine:
git clone https://github.com/sriram750/FIM.git C:\Temp\FIM

# 2. Run the automated installer:
& "C:\Temp\FIM\agent-windows\installer\install.ps1" `
    -ServerUrl "http://192.168.1.50:8000" `
    -EnrollmentToken "change_this_enrollment_token_secret"
```

### What the installer does automatically:
1. Copies agent binaries to `C:\Program Files\FIMEnterprise\Agent`.
2. Creates an isolated Python virtual environment and installs pinned dependencies.
3. Enrolls the endpoint with the central server and receives a unique cryptographic token (`AgentCredential`).
4. Enables Windows Security File System auditing (`auditpol.exe /set /subcategory:"File System" /success:enable /failure:enable`) for actor SID correlation (Event ID 4663).
5. Registers and launches a resilient background SYSTEM task (`FIMEnterpriseAgent`) configured to start at boot and recover automatically if stopped.

---

## 3. Manual Installation & Testing (Step-by-Step)

If you wish to test or run the agent interactively in a console:

### Step 1: Install Dependencies
```powershell
cd C:\Temp\FIM\agent-windows
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2: Enroll Endpoint
Enroll the client with your central FIM server URL and the `ENROLLMENT_TOKEN_SECRET` from `.env`:
```powershell
python src\main.py enroll --server "http://192.168.1.50:8000" --token "change_this_enrollment_token_secret"
```
*Output:*
```
[*] Enrolling host 'DESKTOP-FINANCE-01' with server http://192.168.1.50:8000...
[✓] Successfully enrolled! Assigned Endpoint ID: 3a9c7821-66c5-4a5f-9e77-94d4d2f0eb34
[✓] Cryptographic endpoint token saved to agent_config.json
```

### Step 3: Run Baseline Scan (Optional)
```powershell
python src\main.py scan
```

### Step 4: Start Monitoring Service
```powershell
python src\main.py start
```
*Output:*
```
[*] Starting FIM Enterprise Windows Agent on DESKTOP-FINANCE-01...
[+] Watching directory: C:\Windows\System32\drivers\etc
[+] Watching directory: C:\Program Files\Common Files
[*] Running initial baseline scan...
[+] Initial scan complete: {'files_scanned': 42, 'mismatches': 0, 'new_baselines': 42}
[✓] FIM Agent Service is actively running and monitoring.
```

### Step 5: Check Status at Any Time
```powershell
python src\main.py status
```

---

## 4. Enabling Windows User Attribution (SACL Configuration)

To correlate file change events with the exact Windows user account (Domain\Username and SID), apply a System Access Control List (SACL) to the sensitive folder:

1. Right-click the folder to monitor (e.g., `D:\Confidential` or `C:\Finance`) -> **Properties**.
2. Go to **Security** -> **Advanced** -> **Auditing** tab.
3. Click **Add** -> **Select a principal** -> Type `Everyone` -> Click **OK**.
4. Set:
   - **Type**: `All` (or `Success` and `Fail`)
   - **Applies to**: `This folder, subfolders and files`
   - **Advanced permissions**: Check `Create files / write data`, `Create folders / append data`, `Write attributes`, `Delete`, `Delete subfolders and files`, `Change permissions`.
5. Click **OK** and apply.

Now, whenever a user creates, edits, or deletes a file in this folder, Windows Security Log will generate **Event ID 4663**, and the FIM Agent will capture the Actor SID and Domain\Username!

---

## 5. Enterprise Mass Deployment (Active Directory GPO)

For deploying across 500+ client endpoints:

1. Place the `agent-windows` package and `install.ps1` in your domain NetLogon or network share: `\\CORP.LOCAL\SysVol\CORP.LOCAL\Policies\FIM\`.
2. In **Group Policy Management Console (GPMC)**:
   - Navigate to: `Computer Configuration` -> `Policies` -> `Windows Settings` -> `Scripts (Startup/Shutdown)` -> **Startup**.
   - Add a PowerShell script pointing to:
     ```powershell
     \\CORP.LOCAL\SysVol\CORP.LOCAL\Policies\FIM\installer\install.ps1 -ServerUrl "https://fim.corp.local:8443" -EnrollmentToken "change_this_enrollment_token_secret"
     ```
3. Enable Advanced Audit Policy via GPO:
   - `Computer Configuration` -> `Policies` -> `Windows Settings` -> `Security Settings` -> `Advanced Audit Policy Configuration` -> `Object Access`:
     - **Audit File System**: `Success` and `Failure`.
4. Run `gpupdate /force` on client endpoints. The agent will install silently, register with the server, and begin streaming file integrity baselines immediately.
